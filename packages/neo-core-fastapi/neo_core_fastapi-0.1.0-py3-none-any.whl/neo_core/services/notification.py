"""Notification management services."""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import json

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from pydantic import BaseModel, validator

from .base import BaseService, ServiceException, NotFoundError, ValidationException, DuplicateError
from .crud import NotificationCRUDService
from ..models.notification import (
    Notification, UserNotification, NotificationTemplate, NotificationDeliveryLog
)
from ..models.notification import (
    NotificationType, NotificationPriority, NotificationStatus, DeliveryChannel
)
from ..config import CoreSettings


class NotificationCreateSchema(BaseModel):
    """Schema for creating a notification."""
    title: str
    content: str
    notification_type: NotificationType = NotificationType.INFO
    priority: NotificationPriority = NotificationPriority.NORMAL
    sender_id: Optional[UUID] = None
    application_id: Optional[UUID] = None
    target_users: Optional[List[UUID]] = None
    target_roles: Optional[List[UUID]] = None
    target_groups: Optional[List[UUID]] = None
    delivery_channels: List[DeliveryChannel] = [DeliveryChannel.IN_APP]
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    template_id: Optional[UUID] = None
    template_data: Optional[Dict[str, Any]] = None
    
    @validator('target_users', 'target_roles', 'target_groups')
    def validate_targets(cls, v):
        if v is not None and len(v) == 0:
            return None
        return v


class NotificationUpdateSchema(BaseModel):
    """Schema for updating a notification."""
    title: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[NotificationPriority] = None
    scheduled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    action_url: Optional[str] = None
    action_text: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class NotificationTemplateCreateSchema(BaseModel):
    """Schema for creating a notification template."""
    name: str
    description: Optional[str] = None
    notification_type: NotificationType = NotificationType.INFO
    priority: NotificationPriority = NotificationPriority.NORMAL
    title_template: str
    content_template: str
    delivery_channels: List[DeliveryChannel] = [DeliveryChannel.IN_APP]
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    variables: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    application_id: Optional[UUID] = None
    is_active: bool = True


class NotificationTemplateUpdateSchema(BaseModel):
    """Schema for updating a notification template."""
    name: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[NotificationPriority] = None
    title_template: Optional[str] = None
    content_template: Optional[str] = None
    delivery_channels: Optional[List[DeliveryChannel]] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None
    variables: Optional[Dict[str, str]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class UserNotificationUpdateSchema(BaseModel):
    """Schema for updating user notification."""
    is_read: Optional[bool] = None
    read_at: Optional[datetime] = None
    is_delivered: Optional[bool] = None
    delivered_at: Optional[datetime] = None
    delivery_channel: Optional[DeliveryChannel] = None
    user_action: Optional[str] = None
    action_data: Optional[Dict[str, Any]] = None


class NotificationService(BaseService):
    """Service for notification management."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        self.notification_crud = NotificationCRUDService(settings)
        self.max_notifications_per_user = 1000
        self.default_expiry_days = 30
    
    def create_notification(self, notification_data: NotificationCreateSchema) -> Notification:
        """Create a new notification."""
        try:
            # Validate input
            notification_data = self.validate_input(notification_data, NotificationCreateSchema)
            
            # If using template, render content
            if notification_data.template_id:
                template = self.get_template(notification_data.template_id)
                if not template:
                    raise NotFoundError("NotificationTemplate", notification_data.template_id)
                
                # Render template
                rendered_content = self._render_template(
                    template,
                    notification_data.template_data or {}
                )
                notification_data.title = rendered_content["title"]
                notification_data.content = rendered_content["content"]
                notification_data.notification_type = template.notification_type
                notification_data.priority = template.priority
                notification_data.delivery_channels = template.delivery_channels
                notification_data.category = template.category
                notification_data.tags = template.tags
            
            # Set default expiry if not provided
            if not notification_data.expires_at:
                notification_data.expires_at = datetime.utcnow() + timedelta(days=self.default_expiry_days)
            
            # Create notification data
            create_data = {
                "id": uuid4(),
                "title": notification_data.title,
                "content": notification_data.content,
                "notification_type": notification_data.notification_type,
                "priority": notification_data.priority,
                "status": NotificationStatus.PENDING,
                "sender_id": notification_data.sender_id,
                "application_id": notification_data.application_id,
                "target_users": notification_data.target_users or [],
                "target_roles": notification_data.target_roles or [],
                "target_groups": notification_data.target_groups or [],
                "delivery_channels": notification_data.delivery_channels,
                "scheduled_at": notification_data.scheduled_at or datetime.utcnow(),
                "expires_at": notification_data.expires_at,
                "action_url": notification_data.action_url,
                "action_text": notification_data.action_text,
                "category": notification_data.category,
                "tags": notification_data.tags or [],
                "metadata": notification_data.metadata or {},
                "template_id": notification_data.template_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create notification
            notification = self.notification_crud.create(create_data)
            
            # If scheduled for immediate delivery, process it
            if notification.scheduled_at <= datetime.utcnow():
                self._process_notification(notification)
            
            self.log_operation("create_notification", {
                "notification_id": notification.id,
                "type": notification.notification_type,
                "priority": notification.priority,
                "target_count": len(notification.target_users or [])
            })
            
            return notification
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create notification")
    
    def get_notification(self, notification_id: UUID) -> Optional[Notification]:
        """Get a notification by ID."""
        return self.notification_crud.get(notification_id)
    
    def update_notification(self, notification_id: UUID, notification_data: NotificationUpdateSchema) -> Notification:
        """Update a notification."""
        try:
            # Validate input
            notification_data = self.validate_input(notification_data, NotificationUpdateSchema)
            
            # Get existing notification
            notification = self.notification_crud.get(notification_id)
            if not notification:
                raise NotFoundError("Notification", notification_id)
            
            # Check if notification can be updated
            if notification.status in [NotificationStatus.SENT, NotificationStatus.FAILED]:
                raise ValidationException("Cannot update sent or failed notifications")
            
            # Update notification data
            update_data = notification_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            # Update notification
            updated_notification = self.notification_crud.update(notification_id, update_data)
            
            self.log_operation("update_notification", {
                "notification_id": notification_id,
                "updated_fields": list(update_data.keys())
            })
            
            return updated_notification
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "update notification")
    
    def delete_notification(self, notification_id: UUID) -> bool:
        """Delete a notification."""
        try:
            notification = self.notification_crud.get(notification_id)
            if not notification:
                raise NotFoundError("Notification", notification_id)
            
            # Check if notification can be deleted
            if notification.status == NotificationStatus.SENDING:
                raise ValidationException("Cannot delete notification that is being sent")
            
            # Delete notification
            success = self.notification_crud.delete(notification_id)
            
            if success:
                self.log_operation("delete_notification", {
                    "notification_id": notification_id
                })
            
            return success
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "delete notification")
    
    def send_notification(self, notification_id: UUID) -> bool:
        """Send a notification immediately."""
        try:
            notification = self.notification_crud.get(notification_id)
            if not notification:
                raise NotFoundError("Notification", notification_id)
            
            if notification.status != NotificationStatus.PENDING:
                raise ValidationException("Can only send pending notifications")
            
            # Process notification
            return self._process_notification(notification)
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "send notification")
    
    def cancel_notification(self, notification_id: UUID) -> bool:
        """Cancel a pending notification."""
        try:
            notification = self.notification_crud.get(notification_id)
            if not notification:
                raise NotFoundError("Notification", notification_id)
            
            if notification.status not in [NotificationStatus.PENDING, NotificationStatus.SCHEDULED]:
                raise ValidationException("Can only cancel pending or scheduled notifications")
            
            # Update status
            self.notification_crud.update(notification_id, {
                "status": NotificationStatus.CANCELLED,
                "updated_at": datetime.utcnow()
            })
            
            self.log_operation("cancel_notification", {
                "notification_id": notification_id
            })
            
            return True
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "cancel notification")
    
    def list_notifications(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> List[Notification]:
        """List notifications with filtering and pagination."""
        return self.notification_crud.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=order_by,
            order_desc=order_desc
        )
    
    def get_user_notifications(
        self,
        user_id: UUID,
        unread_only: bool = False,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserNotification]:
        """Get notifications for a user."""
        try:
            query = self.db.query(UserNotification).filter(
                UserNotification.user_id == user_id
            )
            
            if unread_only:
                query = query.filter(UserNotification.is_read == False)
            
            return (
                query.order_by(UserNotification.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            self.handle_db_error(e, "get user notifications")
    
    def mark_notification_read(self, user_id: UUID, notification_id: UUID) -> bool:
        """Mark a notification as read for a user."""
        try:
            user_notification = (
                self.db.query(UserNotification)
                .filter(
                    UserNotification.user_id == user_id,
                    UserNotification.notification_id == notification_id
                )
                .first()
            )
            
            if not user_notification:
                raise NotFoundError("UserNotification", f"{user_id}:{notification_id}")
            
            if not user_notification.is_read:
                user_notification.is_read = True
                user_notification.read_at = datetime.utcnow()
                user_notification.updated_at = datetime.utcnow()
                self.db.commit()
            
            return True
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "mark notification read")
    
    def mark_all_notifications_read(self, user_id: UUID) -> int:
        """Mark all notifications as read for a user."""
        try:
            updated_count = (
                self.db.query(UserNotification)
                .filter(
                    UserNotification.user_id == user_id,
                    UserNotification.is_read == False
                )
                .update({
                    "is_read": True,
                    "read_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                })
            )
            
            self.db.commit()
            
            self.log_operation("mark_all_notifications_read", {
                "user_id": user_id,
                "updated_count": updated_count
            })
            
            return updated_count
        except Exception as e:
            self.db.rollback()
            self.handle_db_error(e, "mark all notifications read")
    
    def get_unread_count(self, user_id: UUID) -> int:
        """Get unread notification count for a user."""
        try:
            return (
                self.db.query(UserNotification)
                .filter(
                    UserNotification.user_id == user_id,
                    UserNotification.is_read == False
                )
                .count()
            )
        except Exception as e:
            self.handle_db_error(e, "get unread count")
    
    def create_template(self, template_data: NotificationTemplateCreateSchema) -> NotificationTemplate:
        """Create a notification template."""
        try:
            # Validate input
            template_data = self.validate_input(template_data, NotificationTemplateCreateSchema)
            
            # Check for duplicate name
            existing = (
                self.db.query(NotificationTemplate)
                .filter(
                    NotificationTemplate.name == template_data.name,
                    NotificationTemplate.application_id == template_data.application_id
                )
                .first()
            )
            
            if existing:
                raise DuplicateError("NotificationTemplate", "name", template_data.name)
            
            # Create template data
            create_data = {
                "id": uuid4(),
                "name": template_data.name,
                "description": template_data.description,
                "notification_type": template_data.notification_type,
                "priority": template_data.priority,
                "title_template": template_data.title_template,
                "content_template": template_data.content_template,
                "delivery_channels": template_data.delivery_channels,
                "category": template_data.category,
                "tags": template_data.tags or [],
                "variables": template_data.variables or {},
                "metadata": template_data.metadata or {},
                "application_id": template_data.application_id,
                "is_active": template_data.is_active,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create template
            template = NotificationTemplate(**create_data)
            self.db.add(template)
            self.db.commit()
            self.db.refresh(template)
            
            self.log_operation("create_notification_template", {
                "template_id": template.id,
                "name": template.name,
                "type": template.notification_type
            })
            
            return template
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create notification template")
    
    def get_template(self, template_id: UUID) -> Optional[NotificationTemplate]:
        """Get a notification template by ID."""
        try:
            return self.db.query(NotificationTemplate).filter(
                NotificationTemplate.id == template_id
            ).first()
        except Exception as e:
            self.handle_db_error(e, "get notification template")
    
    def get_template_by_name(self, name: str, application_id: UUID = None) -> Optional[NotificationTemplate]:
        """Get a notification template by name."""
        try:
            query = self.db.query(NotificationTemplate).filter(
                NotificationTemplate.name == name
            )
            
            if application_id:
                query = query.filter(NotificationTemplate.application_id == application_id)
            
            return query.first()
        except Exception as e:
            self.handle_db_error(e, "get notification template by name")
    
    def update_template(self, template_id: UUID, template_data: NotificationTemplateUpdateSchema) -> NotificationTemplate:
        """Update a notification template."""
        try:
            # Validate input
            template_data = self.validate_input(template_data, NotificationTemplateUpdateSchema)
            
            # Get existing template
            template = self.get_template(template_id)
            if not template:
                raise NotFoundError("NotificationTemplate", template_id)
            
            # Update template data
            update_data = template_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            # Update template
            for key, value in update_data.items():
                setattr(template, key, value)
            
            self.db.commit()
            self.db.refresh(template)
            
            self.log_operation("update_notification_template", {
                "template_id": template_id,
                "updated_fields": list(update_data.keys())
            })
            
            return template
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "update notification template")
    
    def delete_template(self, template_id: UUID) -> bool:
        """Delete a notification template."""
        try:
            template = self.get_template(template_id)
            if not template:
                raise NotFoundError("NotificationTemplate", template_id)
            
            # Check if template is being used
            notifications_using_template = (
                self.db.query(Notification)
                .filter(Notification.template_id == template_id)
                .count()
            )
            
            if notifications_using_template > 0:
                raise ValidationException("Cannot delete template that is being used by notifications")
            
            # Delete template
            self.db.delete(template)
            self.db.commit()
            
            self.log_operation("delete_notification_template", {
                "template_id": template_id
            })
            
            return True
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "delete notification template")
    
    def list_templates(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        order_by: str = "name",
        order_desc: bool = False
    ) -> List[NotificationTemplate]:
        """List notification templates with filtering and pagination."""
        try:
            query = self.db.query(NotificationTemplate)
            
            # Apply filters
            if filters:
                for key, value in filters.items():
                    if hasattr(NotificationTemplate, key):
                        query = query.filter(getattr(NotificationTemplate, key) == value)
            
            # Apply ordering
            if hasattr(NotificationTemplate, order_by):
                order_column = getattr(NotificationTemplate, order_by)
                if order_desc:
                    query = query.order_by(order_column.desc())
                else:
                    query = query.order_by(order_column)
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            self.handle_db_error(e, "list notification templates")
    
    def process_scheduled_notifications(self) -> int:
        """Process scheduled notifications that are due."""
        try:
            current_time = datetime.utcnow()
            
            # Get scheduled notifications that are due
            due_notifications = (
                self.db.query(Notification)
                .filter(
                    Notification.status == NotificationStatus.SCHEDULED,
                    Notification.scheduled_at <= current_time
                )
                .all()
            )
            
            processed_count = 0
            for notification in due_notifications:
                try:
                    self._process_notification(notification)
                    processed_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to process notification {notification.id}: {str(e)}")
                    # Mark as failed
                    self.notification_crud.update(notification.id, {
                        "status": NotificationStatus.FAILED,
                        "error_message": str(e),
                        "updated_at": datetime.utcnow()
                    })
            
            self.log_operation("process_scheduled_notifications", {
                "processed_count": processed_count
            })
            
            return processed_count
        except Exception as e:
            self.handle_db_error(e, "process scheduled notifications")
    
    def cleanup_expired_notifications(self) -> int:
        """Clean up expired notifications."""
        try:
            current_time = datetime.utcnow()
            
            # Delete expired notifications
            deleted_count = (
                self.db.query(Notification)
                .filter(
                    Notification.expires_at < current_time,
                    Notification.status.in_([
                        NotificationStatus.SENT,
                        NotificationStatus.FAILED,
                        NotificationStatus.CANCELLED
                    ])
                )
                .delete()
            )
            
            self.db.commit()
            
            self.log_operation("cleanup_expired_notifications", {
                "deleted_count": deleted_count
            })
            
            return deleted_count
        except Exception as e:
            self.db.rollback()
            self.handle_db_error(e, "cleanup expired notifications")
    
    def _process_notification(self, notification: Notification) -> bool:
        """Process a notification for delivery."""
        try:
            # Update status to sending
            self.notification_crud.update(notification.id, {
                "status": NotificationStatus.SENDING,
                "sent_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            # Get target users
            target_users = self._resolve_target_users(notification)
            
            if not target_users:
                # No target users, mark as sent
                self.notification_crud.update(notification.id, {
                    "status": NotificationStatus.SENT,
                    "updated_at": datetime.utcnow()
                })
                return True
            
            # Create user notifications
            success_count = 0
            for user_id in target_users:
                try:
                    self._create_user_notification(notification, user_id)
                    success_count += 1
                except Exception as e:
                    self.logger.error(f"Failed to create user notification for user {user_id}: {str(e)}")
            
            # Update notification status
            if success_count > 0:
                self.notification_crud.update(notification.id, {
                    "status": NotificationStatus.SENT,
                    "recipient_count": success_count,
                    "updated_at": datetime.utcnow()
                })
            else:
                self.notification_crud.update(notification.id, {
                    "status": NotificationStatus.FAILED,
                    "error_message": "No users could receive the notification",
                    "updated_at": datetime.utcnow()
                })
            
            return success_count > 0
        except Exception as e:
            # Mark as failed
            self.notification_crud.update(notification.id, {
                "status": NotificationStatus.FAILED,
                "error_message": str(e),
                "updated_at": datetime.utcnow()
            })
            raise
    
    def _resolve_target_users(self, notification: Notification) -> List[UUID]:
        """Resolve target users from notification targets."""
        target_users = set()
        
        # Direct user targets
        if notification.target_users:
            target_users.update(notification.target_users)
        
        # Role-based targets
        if notification.target_roles:
            # This would require integration with role service
            # For now, we'll skip this implementation
            pass
        
        # Group-based targets
        if notification.target_groups:
            # This would require integration with group service
            # For now, we'll skip this implementation
            pass
        
        return list(target_users)
    
    def _create_user_notification(self, notification: Notification, user_id: UUID) -> UserNotification:
        """Create a user notification."""
        user_notification_data = {
            "id": uuid4(),
            "notification_id": notification.id,
            "user_id": user_id,
            "is_read": False,
            "is_delivered": True,
            "delivered_at": datetime.utcnow(),
            "delivery_channel": DeliveryChannel.IN_APP,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        user_notification = UserNotification(**user_notification_data)
        self.db.add(user_notification)
        self.db.commit()
        self.db.refresh(user_notification)
        
        return user_notification
    
    def _render_template(self, template: NotificationTemplate, data: Dict[str, Any]) -> Dict[str, str]:
        """Render a notification template with data."""
        try:
            # Simple template rendering (could be enhanced with Jinja2)
            title = template.title_template
            content = template.content_template
            
            # Replace variables
            for key, value in data.items():
                placeholder = f"{{{key}}}"
                title = title.replace(placeholder, str(value))
                content = content.replace(placeholder, str(value))
            
            return {
                "title": title,
                "content": content
            }
        except Exception as e:
            raise ValidationException(f"Failed to render template: {str(e)}")
    
    def get_notification_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get notification statistics."""
        try:
            # Default to last 30 days if no time range specified
            if not start_time:
                start_time = datetime.utcnow() - timedelta(days=30)
            if not end_time:
                end_time = datetime.utcnow()
            
            # Base query
            query = self.db.query(Notification).filter(
                Notification.created_at >= start_time,
                Notification.created_at <= end_time
            )
            
            # Total notifications
            total_notifications = query.count()
            
            # Notifications by status
            status_counts = {}
            for status in NotificationStatus:
                count = query.filter(Notification.status == status).count()
                status_counts[status.value] = count
            
            # Notifications by type
            type_counts = {}
            for notification_type in NotificationType:
                count = query.filter(Notification.notification_type == notification_type).count()
                type_counts[notification_type.value] = count
            
            # Notifications by priority
            priority_counts = {}
            for priority in NotificationPriority:
                count = query.filter(Notification.priority == priority).count()
                priority_counts[priority.value] = count
            
            # Delivery rate
            sent_count = query.filter(Notification.status == NotificationStatus.SENT).count()
            delivery_rate = (sent_count / total_notifications * 100) if total_notifications > 0 else 0
            
            return {
                "period": {
                    "start_time": start_time,
                    "end_time": end_time
                },
                "total_notifications": total_notifications,
                "status_counts": status_counts,
                "type_counts": type_counts,
                "priority_counts": priority_counts,
                "delivery_rate": delivery_rate
            }
        except Exception as e:
            self.handle_db_error(e, "get notification statistics")