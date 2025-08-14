"""Notification models for managing system notifications and messaging."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ..database.base import BaseModel
from ..database.mixins import TimestampMixin, SoftDeleteMixin


class NotificationType(str, Enum):
    """Notification type enumeration."""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ALERT = "alert"
    REMINDER = "reminder"
    ANNOUNCEMENT = "announcement"
    SYSTEM = "system"
    SECURITY = "security"
    MARKETING = "marketing"
    SOCIAL = "social"
    TASK = "task"
    MESSAGE = "message"


class NotificationPriority(str, Enum):
    """Notification priority enumeration."""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class NotificationStatus(str, Enum):
    """Notification status enumeration."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


class DeliveryChannel(str, Enum):
    """Delivery channel enumeration."""
    IN_APP = "in_app"
    EMAIL = "email"
    SMS = "sms"
    PUSH = "push"
    WEBHOOK = "webhook"
    SLACK = "slack"
    TEAMS = "teams"
    DISCORD = "discord"
    TELEGRAM = "telegram"


# Association table for notification recipients
notification_recipients = Table(
    'notification_recipients',
    BaseModel.metadata,
    Column('notification_id', UUID(as_uuid=True), ForeignKey('notification.id'), primary_key=True),
    Column('user_id', UUID(as_uuid=True), ForeignKey('user.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), default=datetime.utcnow)
)


class Notification(BaseModel, TimestampMixin, SoftDeleteMixin):
    """Notification model for managing system notifications."""
    
    __tablename__ = "notification"
    
    # Basic information
    title = Column(
        String(200),
        nullable=False,
        comment="Notification title"
    )
    
    message = Column(
        Text,
        nullable=False,
        comment="Notification message content"
    )
    
    # Notification properties
    notification_type = Column(
        String(20),
        default=NotificationType.INFO,
        nullable=False,
        index=True,
        comment="Notification type"
    )
    
    priority = Column(
        String(20),
        default=NotificationPriority.NORMAL,
        nullable=False,
        index=True,
        comment="Notification priority"
    )
    
    status = Column(
        String(20),
        default=NotificationStatus.PENDING,
        nullable=False,
        index=True,
        comment="Notification status"
    )
    
    # Sender information
    sender_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=True,
        comment="Sender user ID"
    )
    
    sender_name = Column(
        String(100),
        nullable=True,
        comment="Sender display name"
    )
    
    sender_type = Column(
        String(50),
        default="user",
        nullable=False,
        comment="Sender type (user, system, service)"
    )
    
    # Application context
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("application.id"),
        nullable=True,
        comment="Application ID"
    )
    
    module_name = Column(
        String(100),
        nullable=True,
        comment="Module name that generated notification"
    )
    
    # Scheduling
    scheduled_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Scheduled delivery time"
    )
    
    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Notification expiration time"
    )
    
    # Delivery settings
    delivery_channels = Column(
        JSONB,
        nullable=True,
        comment="Delivery channels configuration"
    )
    
    delivery_attempts = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of delivery attempts"
    )
    
    max_delivery_attempts = Column(
        Integer,
        default=3,
        nullable=False,
        comment="Maximum delivery attempts"
    )
    
    # Content and formatting
    content_html = Column(
        Text,
        nullable=True,
        comment="HTML formatted content"
    )
    
    content_markdown = Column(
        Text,
        nullable=True,
        comment="Markdown formatted content"
    )
    
    # Actions and links
    action_url = Column(
        String(500),
        nullable=True,
        comment="Action URL for notification"
    )
    
    action_text = Column(
        String(100),
        nullable=True,
        comment="Action button text"
    )
    
    actions = Column(
        JSONB,
        nullable=True,
        comment="Additional actions configuration"
    )
    
    # Grouping and categorization
    category = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Notification category"
    )
    
    group_key = Column(
        String(200),
        nullable=True,
        index=True,
        comment="Grouping key for related notifications"
    )
    
    tags = Column(
        String(500),
        nullable=True,
        comment="Comma-separated tags"
    )
    
    # Tracking and analytics
    sent_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Actual send time"
    )
    
    delivered_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Delivery confirmation time"
    )
    
    # Additional data
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional notification metadata"
    )
    
    # Relationships
    sender = relationship(
        "User",
        foreign_keys=[sender_id]
    )
    
    application = relationship(
        "Application"
    )
    
    recipients = relationship(
        "User",
        secondary=notification_recipients,
        back_populates="notifications"
    )
    
    user_notifications = relationship(
        "UserNotification",
        back_populates="notification",
        cascade="all, delete-orphan"
    )
    
    delivery_logs = relationship(
        "NotificationDeliveryLog",
        back_populates="notification",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Notification(id={self.id}, title={self.title}, type={self.notification_type})>"
    
    @property
    def is_scheduled(self) -> bool:
        """Check if notification is scheduled for future delivery."""
        return self.scheduled_at and self.scheduled_at > datetime.utcnow()
    
    @property
    def is_expired(self) -> bool:
        """Check if notification is expired."""
        return self.expires_at and self.expires_at <= datetime.utcnow()
    
    @property
    def is_deliverable(self) -> bool:
        """Check if notification can be delivered."""
        return (
            self.status in [NotificationStatus.PENDING, NotificationStatus.FAILED] and
            not self.is_expired and
            self.delivery_attempts < self.max_delivery_attempts
        )
    
    @property
    def recipient_count(self) -> int:
        """Get count of recipients."""
        return len(self.recipients)
    
    def add_recipient(self, user_id: str) -> 'UserNotification':
        """Add recipient to notification."""
        user_notification = UserNotification(
            notification_id=self.id,
            user_id=user_id
        )
        self.user_notifications.append(user_notification)
        return user_notification
    
    def remove_recipient(self, user_id: str) -> bool:
        """Remove recipient from notification."""
        for user_notif in self.user_notifications:
            if str(user_notif.user_id) == str(user_id):
                self.user_notifications.remove(user_notif)
                return True
        return False
    
    def mark_as_sent(self, sent_time: datetime = None) -> None:
        """Mark notification as sent."""
        self.status = NotificationStatus.SENT
        self.sent_at = sent_time or datetime.utcnow()
    
    def mark_as_delivered(self, delivered_time: datetime = None) -> None:
        """Mark notification as delivered."""
        self.status = NotificationStatus.DELIVERED
        self.delivered_at = delivered_time or datetime.utcnow()
    
    def mark_as_failed(self, error_message: str = None) -> None:
        """Mark notification as failed."""
        self.status = NotificationStatus.FAILED
        self.delivery_attempts += 1
        if error_message:
            self.add_metadata("last_error", error_message)
    
    def cancel(self, reason: str = None) -> None:
        """Cancel the notification."""
        self.status = NotificationStatus.CANCELLED
        if reason:
            self.add_metadata("cancellation_reason", reason)
    
    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata entry."""
        if self.metadata is None:
            self.metadata = {}
        self.metadata[key] = value
    
    def get_metadata(self, key: str, default=None):
        """Get metadata value."""
        if self.metadata and key in self.metadata:
            return self.metadata[key]
        return default
    
    def add_tag(self, tag: str) -> None:
        """Add tag to notification."""
        if self.tags:
            tags = [t.strip() for t in self.tags.split(",") if t.strip()]
            if tag not in tags:
                tags.append(tag)
                self.tags = ",".join(tags)
        else:
            self.tags = tag
    
    def get_tags(self) -> List[str]:
        """Get list of tags."""
        if self.tags:
            return [t.strip() for t in self.tags.split(",") if t.strip()]
        return []
    
    def log_delivery_attempt(self, channel: str, status: str, error_message: str = None) -> 'NotificationDeliveryLog':
        """Log delivery attempt."""
        log = NotificationDeliveryLog(
            notification_id=self.id,
            channel=channel,
            status=status,
            error_message=error_message
        )
        self.delivery_logs.append(log)
        return log


class UserNotification(BaseModel, TimestampMixin):
    """User notification model for tracking individual user notification status."""
    
    __tablename__ = "user_notification"
    
    # Foreign keys
    notification_id = Column(
        UUID(as_uuid=True),
        ForeignKey("notification.id"),
        nullable=False,
        index=True,
        comment="Notification ID"
    )
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=False,
        index=True,
        comment="User ID"
    )
    
    # Status tracking
    status = Column(
        String(20),
        default=NotificationStatus.PENDING,
        nullable=False,
        index=True,
        comment="User-specific notification status"
    )
    
    is_read = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="User has read the notification"
    )
    
    read_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Time when user read the notification"
    )
    
    # Delivery tracking
    delivered_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Delivery time for this user"
    )
    
    delivery_channel = Column(
        String(20),
        nullable=True,
        comment="Channel used for delivery"
    )
    
    # User actions
    dismissed = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="User dismissed the notification"
    )
    
    dismissed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Time when user dismissed notification"
    )
    
    clicked = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="User clicked on the notification"
    )
    
    clicked_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Time when user clicked notification"
    )
    
    # Additional data
    metadata = Column(
        JSONB,
        nullable=True,
        comment="User-specific notification metadata"
    )
    
    # Relationships
    notification = relationship(
        "Notification",
        back_populates="user_notifications"
    )
    
    user = relationship(
        "User"
    )
    
    def __repr__(self) -> str:
        return f"<UserNotification(id={self.id}, user_id={self.user_id}, read={self.is_read})>"
    
    def mark_as_read(self, read_time: datetime = None) -> None:
        """Mark notification as read by user."""
        self.is_read = True
        self.read_at = read_time or datetime.utcnow()
        if self.status == NotificationStatus.DELIVERED:
            self.status = NotificationStatus.READ
    
    def mark_as_delivered(self, channel: str, delivered_time: datetime = None) -> None:
        """Mark notification as delivered to user."""
        self.status = NotificationStatus.DELIVERED
        self.delivery_channel = channel
        self.delivered_at = delivered_time or datetime.utcnow()
    
    def dismiss(self, dismissed_time: datetime = None) -> None:
        """Dismiss the notification."""
        self.dismissed = True
        self.dismissed_at = dismissed_time or datetime.utcnow()
    
    def click(self, clicked_time: datetime = None) -> None:
        """Record notification click."""
        self.clicked = True
        self.clicked_at = clicked_time or datetime.utcnow()
        if not self.is_read:
            self.mark_as_read(clicked_time)


class NotificationTemplate(BaseModel, TimestampMixin, SoftDeleteMixin):
    """Notification template model for reusable notification templates."""
    
    __tablename__ = "notification_template"
    
    # Template identification
    name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Template name"
    )
    
    display_name = Column(
        String(200),
        nullable=True,
        comment="Human-readable template name"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Template description"
    )
    
    # Template properties
    notification_type = Column(
        String(20),
        default=NotificationType.INFO,
        nullable=False,
        comment="Default notification type"
    )
    
    priority = Column(
        String(20),
        default=NotificationPriority.NORMAL,
        nullable=False,
        comment="Default priority"
    )
    
    category = Column(
        String(100),
        nullable=True,
        comment="Template category"
    )
    
    # Template content
    title_template = Column(
        Text,
        nullable=False,
        comment="Title template with placeholders"
    )
    
    message_template = Column(
        Text,
        nullable=False,
        comment="Message template with placeholders"
    )
    
    html_template = Column(
        Text,
        nullable=True,
        comment="HTML template with placeholders"
    )
    
    # Template configuration
    variables = Column(
        JSONB,
        nullable=True,
        comment="Template variables definition"
    )
    
    default_values = Column(
        JSONB,
        nullable=True,
        comment="Default values for variables"
    )
    
    # Delivery settings
    default_channels = Column(
        JSONB,
        nullable=True,
        comment="Default delivery channels"
    )
    
    # Application context
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("application.id"),
        nullable=True,
        comment="Application ID"
    )
    
    # Template metadata
    version = Column(
        String(20),
        default="1.0.0",
        nullable=False,
        comment="Template version"
    )
    
    is_system = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="System template (cannot be deleted)"
    )
    
    # Usage tracking
    usage_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of times template was used"
    )
    
    last_used_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last usage timestamp"
    )
    
    # Relationships
    application = relationship(
        "Application"
    )
    
    def __repr__(self) -> str:
        return f"<NotificationTemplate(id={self.id}, name={self.name}, type={self.notification_type})>"
    
    def render(self, variables: Dict[str, Any] = None) -> Dict[str, str]:
        """Render template with provided variables."""
        render_vars = self.default_values.copy() if self.default_values else {}
        if variables:
            render_vars.update(variables)
        
        # Simple template rendering (in production, use Jinja2 or similar)
        title = self.title_template
        message = self.message_template
        html = self.html_template
        
        for key, value in render_vars.items():
            placeholder = f"{{{key}}}"
            title = title.replace(placeholder, str(value)) if title else title
            message = message.replace(placeholder, str(value)) if message else message
            html = html.replace(placeholder, str(value)) if html else html
        
        return {
            "title": title,
            "message": message,
            "html": html
        }
    
    def create_notification(self, variables: Dict[str, Any] = None, **kwargs) -> Notification:
        """Create notification from template."""
        rendered = self.render(variables)
        
        notification = Notification(
            title=rendered["title"],
            message=rendered["message"],
            content_html=rendered["html"],
            notification_type=self.notification_type,
            priority=self.priority,
            category=self.category,
            delivery_channels=self.default_channels,
            application_id=self.application_id,
            **kwargs
        )
        
        # Update usage tracking
        self.usage_count += 1
        self.last_used_at = datetime.utcnow()
        
        return notification


class NotificationDeliveryLog(BaseModel, TimestampMixin):
    """Notification delivery log model for tracking delivery attempts."""
    
    __tablename__ = "notification_delivery_log"
    
    # Foreign key
    notification_id = Column(
        UUID(as_uuid=True),
        ForeignKey("notification.id"),
        nullable=False,
        index=True,
        comment="Notification ID"
    )
    
    # Delivery information
    channel = Column(
        String(20),
        nullable=False,
        comment="Delivery channel used"
    )
    
    status = Column(
        String(20),
        nullable=False,
        comment="Delivery status"
    )
    
    # Error information
    error_message = Column(
        Text,
        nullable=True,
        comment="Error message if delivery failed"
    )
    
    error_code = Column(
        String(50),
        nullable=True,
        comment="Error code"
    )
    
    # Delivery details
    provider = Column(
        String(100),
        nullable=True,
        comment="Service provider used for delivery"
    )
    
    provider_message_id = Column(
        String(255),
        nullable=True,
        comment="Provider's message ID"
    )
    
    # Performance metrics
    duration_ms = Column(
        Integer,
        nullable=True,
        comment="Delivery duration in milliseconds"
    )
    
    # Additional data
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional delivery metadata"
    )
    
    # Relationships
    notification = relationship(
        "Notification",
        back_populates="delivery_logs"
    )
    
    def __repr__(self) -> str:
        return f"<NotificationDeliveryLog(id={self.id}, channel={self.channel}, status={self.status})>"