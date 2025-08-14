"""Email service for sending emails."""

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import smtplib
import ssl
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import jinja2
from pydantic import BaseModel, EmailStr, validator

from .base import BaseService, ServiceException
from ..config import CoreSettings


class EmailException(ServiceException):
    """Email-related exception."""
    pass


class EmailConfigurationError(EmailException):
    """Email configuration error."""
    pass


class EmailSendError(EmailException):
    """Email send error."""
    pass


class EmailTemplateError(EmailException):
    """Email template error."""
    pass


class EmailAttachment(BaseModel):
    """Email attachment model."""
    filename: str
    content: bytes
    content_type: str = "application/octet-stream"
    
    class Config:
        arbitrary_types_allowed = True


class EmailMessage(BaseModel):
    """Email message model."""
    to: List[EmailStr]
    subject: str
    body: str
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None
    reply_to: Optional[EmailStr] = None
    attachments: Optional[List[EmailAttachment]] = None
    is_html: bool = False
    priority: str = "normal"  # low, normal, high
    
    @validator('priority')
    def validate_priority(cls, v):
        if v not in ['low', 'normal', 'high']:
            raise ValueError('Priority must be low, normal, or high')
        return v


class EmailTemplate(BaseModel):
    """Email template model."""
    name: str
    subject_template: str
    body_template: str
    is_html: bool = False
    description: Optional[str] = None
    variables: Optional[List[str]] = None
    created_at: datetime = None
    updated_at: datetime = None
    
    def __init__(self, **data):
        if 'created_at' not in data:
            data['created_at'] = datetime.utcnow()
        if 'updated_at' not in data:
            data['updated_at'] = datetime.utcnow()
        super().__init__(**data)


class SMTPConfig(BaseModel):
    """SMTP configuration model."""
    host: str
    port: int = 587
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: bool = True
    use_ssl: bool = False
    timeout: int = 30
    
    @validator('port')
    def validate_port(cls, v):
        if not 1 <= v <= 65535:
            raise ValueError('Port must be between 1 and 65535')
        return v


class EmailService(BaseService):
    """Email service for sending emails."""
    
    def __init__(self, settings: CoreSettings = None, smtp_config: SMTPConfig = None):
        super().__init__(settings)
        
        # SMTP configuration
        if smtp_config:
            self.smtp_config = smtp_config
        else:
            self.smtp_config = SMTPConfig(
                host=getattr(self.settings, 'SMTP_HOST', 'localhost'),
                port=getattr(self.settings, 'SMTP_PORT', 587),
                username=getattr(self.settings, 'SMTP_USERNAME', None),
                password=getattr(self.settings, 'SMTP_PASSWORD', None),
                use_tls=getattr(self.settings, 'SMTP_USE_TLS', True),
                use_ssl=getattr(self.settings, 'SMTP_USE_SSL', False),
                timeout=getattr(self.settings, 'SMTP_TIMEOUT', 30)
            )
        
        # Email settings
        self.from_email = getattr(self.settings, 'EMAIL_FROM', 'noreply@example.com')
        self.from_name = getattr(self.settings, 'EMAIL_FROM_NAME', 'Neo Core')
        self.reply_to = getattr(self.settings, 'EMAIL_REPLY_TO', None)
        
        # Template settings
        self.template_dir = getattr(self.settings, 'EMAIL_TEMPLATE_DIR', None)
        self.templates: Dict[str, EmailTemplate] = {}
        
        # Initialize Jinja2 environment
        if self.template_dir and Path(self.template_dir).exists():
            self.jinja_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(self.template_dir),
                autoescape=jinja2.select_autoescape(['html', 'xml'])
            )
        else:
            self.jinja_env = jinja2.Environment(
                loader=jinja2.DictLoader({}),
                autoescape=jinja2.select_autoescape(['html', 'xml'])
            )
        
        # Thread pool for async email sending
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        self.logger.info("Email service initialized")
    
    def _create_smtp_connection(self) -> smtplib.SMTP:
        """Create SMTP connection."""
        try:
            if self.smtp_config.use_ssl:
                # Use SMTP_SSL for SSL connections
                context = ssl.create_default_context()
                smtp = smtplib.SMTP_SSL(
                    self.smtp_config.host,
                    self.smtp_config.port,
                    timeout=self.smtp_config.timeout,
                    context=context
                )
            else:
                # Use regular SMTP
                smtp = smtplib.SMTP(
                    self.smtp_config.host,
                    self.smtp_config.port,
                    timeout=self.smtp_config.timeout
                )
                
                if self.smtp_config.use_tls:
                    smtp.starttls()
            
            # Authenticate if credentials provided
            if self.smtp_config.username and self.smtp_config.password:
                smtp.login(self.smtp_config.username, self.smtp_config.password)
            
            return smtp
        except Exception as e:
            raise EmailConfigurationError(f"Failed to create SMTP connection: {str(e)}")
    
    def _create_message(self, email: EmailMessage) -> MIMEMultipart:
        """Create email message."""
        try:
            # Create message
            msg = MIMEMultipart('alternative' if email.is_html else 'mixed')
            
            # Set headers
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = ', '.join(email.to)
            msg['Subject'] = email.subject
            
            if email.cc:
                msg['Cc'] = ', '.join(email.cc)
            
            if email.reply_to:
                msg['Reply-To'] = email.reply_to
            elif self.reply_to:
                msg['Reply-To'] = self.reply_to
            
            # Set priority
            if email.priority == 'high':
                msg['X-Priority'] = '1'
                msg['X-MSMail-Priority'] = 'High'
            elif email.priority == 'low':
                msg['X-Priority'] = '5'
                msg['X-MSMail-Priority'] = 'Low'
            
            # Add body
            if email.is_html:
                body_part = MIMEText(email.body, 'html', 'utf-8')
            else:
                body_part = MIMEText(email.body, 'plain', 'utf-8')
            
            msg.attach(body_part)
            
            # Add attachments
            if email.attachments:
                for attachment in email.attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment.content)
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment.filename}'
                    )
                    part.add_header('Content-Type', attachment.content_type)
                    msg.attach(part)
            
            return msg
        except Exception as e:
            raise EmailSendError(f"Failed to create email message: {str(e)}")
    
    def send_email(self, email: EmailMessage) -> bool:
        """Send email synchronously."""
        try:
            # Create SMTP connection
            smtp = self._create_smtp_connection()
            
            try:
                # Create message
                msg = self._create_message(email)
                
                # Get all recipients
                recipients = list(email.to)
                if email.cc:
                    recipients.extend(email.cc)
                if email.bcc:
                    recipients.extend(email.bcc)
                
                # Send email
                smtp.send_message(msg, to_addrs=recipients)
                
                self.logger.info(f"Email sent successfully to {', '.join(email.to)}")
                return True
            finally:
                smtp.quit()
        except Exception as e:
            self.logger.error(f"Failed to send email: {str(e)}")
            raise EmailSendError(f"Failed to send email: {str(e)}")
    
    async def send_email_async(self, email: EmailMessage) -> bool:
        """Send email asynchronously."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.send_email, email)
    
    def send_bulk_emails(self, emails: List[EmailMessage]) -> Dict[str, Any]:
        """Send multiple emails."""
        results = {
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        for email in emails:
            try:
                self.send_email(email)
                results['sent'] += 1
            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'recipients': email.to,
                    'error': str(e)
                })
        
        return results
    
    async def send_bulk_emails_async(self, emails: List[EmailMessage]) -> Dict[str, Any]:
        """Send multiple emails asynchronously."""
        tasks = [self.send_email_async(email) for email in emails]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        summary = {
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                summary['failed'] += 1
                summary['errors'].append({
                    'recipients': emails[i].to,
                    'error': str(result)
                })
            else:
                summary['sent'] += 1
        
        return summary
    
    def create_template(self, template: EmailTemplate) -> EmailTemplate:
        """Create email template."""
        try:
            # Validate template by trying to render it
            self._validate_template(template)
            
            # Store template
            self.templates[template.name] = template
            
            # Add to Jinja2 environment
            self.jinja_env.get_or_select_template = lambda name: self.jinja_env.from_string(
                self.templates[name].body_template
            )
            
            self.logger.info(f"Email template '{template.name}' created")
            return template
        except Exception as e:
            raise EmailTemplateError(f"Failed to create template: {str(e)}")
    
    def get_template(self, name: str) -> Optional[EmailTemplate]:
        """Get email template by name."""
        return self.templates.get(name)
    
    def list_templates(self) -> List[EmailTemplate]:
        """List all email templates."""
        return list(self.templates.values())
    
    def update_template(self, name: str, template: EmailTemplate) -> EmailTemplate:
        """Update email template."""
        if name not in self.templates:
            raise EmailTemplateError(f"Template '{name}' not found")
        
        try:
            # Validate template
            self._validate_template(template)
            
            # Update template
            template.updated_at = datetime.utcnow()
            self.templates[name] = template
            
            self.logger.info(f"Email template '{name}' updated")
            return template
        except Exception as e:
            raise EmailTemplateError(f"Failed to update template: {str(e)}")
    
    def delete_template(self, name: str) -> bool:
        """Delete email template."""
        if name not in self.templates:
            return False
        
        del self.templates[name]
        self.logger.info(f"Email template '{name}' deleted")
        return True
    
    def render_template(self, template_name: str, variables: Dict[str, Any]) -> EmailMessage:
        """Render email template with variables."""
        template = self.get_template(template_name)
        if not template:
            raise EmailTemplateError(f"Template '{template_name}' not found")
        
        try:
            # Render subject
            subject_template = jinja2.Template(template.subject_template)
            subject = subject_template.render(**variables)
            
            # Render body
            body_template = jinja2.Template(template.body_template)
            body = body_template.render(**variables)
            
            # Create email message (without recipients)
            return EmailMessage(
                to=[],  # Will be set by caller
                subject=subject,
                body=body,
                is_html=template.is_html
            )
        except Exception as e:
            raise EmailTemplateError(f"Failed to render template: {str(e)}")
    
    def send_template_email(
        self,
        template_name: str,
        to: List[EmailStr],
        variables: Dict[str, Any],
        cc: Optional[List[EmailStr]] = None,
        bcc: Optional[List[EmailStr]] = None,
        attachments: Optional[List[EmailAttachment]] = None
    ) -> bool:
        """Send email using template."""
        try:
            # Render template
            email = self.render_template(template_name, variables)
            
            # Set recipients and other options
            email.to = to
            email.cc = cc
            email.bcc = bcc
            email.attachments = attachments
            
            # Send email
            return self.send_email(email)
        except Exception as e:
            raise EmailSendError(f"Failed to send template email: {str(e)}")
    
    async def send_template_email_async(
        self,
        template_name: str,
        to: List[EmailStr],
        variables: Dict[str, Any],
        cc: Optional[List[EmailStr]] = None,
        bcc: Optional[List[EmailStr]] = None,
        attachments: Optional[List[EmailAttachment]] = None
    ) -> bool:
        """Send email using template asynchronously."""
        try:
            # Render template
            email = self.render_template(template_name, variables)
            
            # Set recipients and other options
            email.to = to
            email.cc = cc
            email.bcc = bcc
            email.attachments = attachments
            
            # Send email
            return await self.send_email_async(email)
        except Exception as e:
            raise EmailSendError(f"Failed to send template email: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test SMTP connection."""
        try:
            smtp = self._create_smtp_connection()
            smtp.quit()
            return True
        except Exception as e:
            self.logger.error(f"SMTP connection test failed: {str(e)}")
            return False
    
    def _validate_template(self, template: EmailTemplate) -> None:
        """Validate email template."""
        try:
            # Test subject template
            subject_template = jinja2.Template(template.subject_template)
            subject_template.render()
            
            # Test body template
            body_template = jinja2.Template(template.body_template)
            body_template.render()
        except jinja2.TemplateError as e:
            raise EmailTemplateError(f"Template validation failed: {str(e)}")
    
    def create_attachment_from_file(self, file_path: Union[str, Path]) -> EmailAttachment:
        """Create email attachment from file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise EmailException(f"File not found: {file_path}")
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Determine content type
            content_type = "application/octet-stream"
            suffix = file_path.suffix.lower()
            
            content_type_map = {
                '.txt': 'text/plain',
                '.pdf': 'application/pdf',
                '.doc': 'application/msword',
                '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                '.xls': 'application/vnd.ms-excel',
                '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.png': 'image/png',
                '.gif': 'image/gif',
                '.zip': 'application/zip',
                '.csv': 'text/csv'
            }
            
            content_type = content_type_map.get(suffix, content_type)
            
            return EmailAttachment(
                filename=file_path.name,
                content=content,
                content_type=content_type
            )
        except Exception as e:
            raise EmailException(f"Failed to create attachment from file: {str(e)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get email service statistics."""
        return {
            "smtp_host": self.smtp_config.host,
            "smtp_port": self.smtp_config.port,
            "from_email": self.from_email,
            "templates_count": len(self.templates),
            "template_names": list(self.templates.keys())
        }
    
    def health_check(self) -> Dict[str, Any]:
        """Check email service health."""
        try:
            connection_ok = self.test_connection()
            
            return {
                "healthy": connection_ok,
                "smtp_connection": connection_ok,
                "templates_loaded": len(self.templates)
            }
        except Exception as e:
            return {
                "healthy": False,
                "error": str(e)
            }