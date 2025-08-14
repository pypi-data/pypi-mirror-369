"""CRUD service implementations for core models."""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from pydantic import BaseModel

from .base import CRUDService, ServiceException, NotFoundError, ValidationException
from ..models.user import User, UserProfile, UserPreference
from ..models.role import Role, RolePermission
from ..models.permission import Permission, PermissionGroup
from ..models.application import Application, ApplicationModule, ApplicationConfig
from ..models.audit import AuditLog, AuditTrail
from ..models.session import UserSession, SessionActivity, RefreshToken
from ..models.notification import Notification, UserNotification, NotificationTemplate
from ..models.file import File, FileVersion, FileShare, FileAccessLog
from ..config import CoreSettings


class UserCRUDService(CRUDService[User, BaseModel, BaseModel]):
    """CRUD service for User model."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(User, settings)
    
    def get_by_username(self, username: str) -> Optional[User]:
        """Get user by username."""
        return self.get_by_field("username", username)
    
    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email."""
        return self.get_by_field("email", email)
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Get active users."""
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"is_active": True, "is_deleted": False}
        )
    
    def get_users_by_role(self, role_id: UUID, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role."""
        try:
            return (
                self.db.query(User)
                .join(User.roles)
                .filter(Role.id == role_id)
                .filter(User.is_active == True)
                .filter(User.is_deleted == False)
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            self.handle_db_error(e, "get users by role")
    
    def search_users(
        self,
        search_term: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[User]:
        """Search users by username, email, or full name."""
        return self.search(
            search_term=search_term,
            search_fields=["username", "email", "first_name", "last_name"],
            skip=skip,
            limit=limit
        )
    
    def update_last_login(self, user_id: UUID, ip_address: str = None) -> User:
        """Update user's last login information."""
        try:
            user = self.get(user_id)
            if not user:
                raise NotFoundError("User", user_id)
            
            user.last_login_at = datetime.utcnow()
            user.login_count = (user.login_count or 0) + 1
            
            if ip_address:
                user.last_login_ip = ip_address
            
            self.db.commit()
            self.db.refresh(user)
            
            return user
        except Exception as e:
            self.db.rollback()
            self.handle_db_error(e, "update last login")


class UserProfileCRUDService(CRUDService[UserProfile, BaseModel, BaseModel]):
    """CRUD service for UserProfile model."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(UserProfile, settings)
    
    def get_by_user_id(self, user_id: UUID) -> Optional[UserProfile]:
        """Get profile by user ID."""
        return self.get_by_field("user_id", user_id)


class UserPreferenceCRUDService(CRUDService[UserPreference, BaseModel, BaseModel]):
    """CRUD service for UserPreference model."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(UserPreference, settings)
    
    def get_by_user_id(self, user_id: UUID) -> Optional[UserPreference]:
        """Get preferences by user ID."""
        return self.get_by_field("user_id", user_id)


class RoleCRUDService(CRUDService[Role, BaseModel, BaseModel]):
    """CRUD service for Role model."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(Role, settings)
    
    def get_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        return self.get_by_field("name", name)
    
    def get_by_code(self, code: str) -> Optional[Role]:
        """Get role by code."""
        return self.get_by_field("code", code)
    
    def get_active_roles(self, skip: int = 0, limit: int = 100) -> List[Role]:
        """Get active roles."""
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"is_active": True, "is_deleted": False}
        )
    
    def get_roles_by_application(self, application_id: UUID) -> List[Role]:
        """Get roles by application."""
        return self.get_multi(filters={"application_id": application_id})
    
    def get_role_hierarchy(self, role_id: UUID) -> List[Role]:
        """Get role hierarchy (parent and child roles)."""
        try:
            role = self.get(role_id)
            if not role:
                raise NotFoundError("Role", role_id)
            
            # Get all parent and child roles
            hierarchy = [role]
            
            # Add parent roles
            current_role = role
            while current_role.parent_role:
                hierarchy.insert(0, current_role.parent_role)
                current_role = current_role.parent_role
            
            # Add child roles (recursive)
            def add_children(parent_role):
                for child in parent_role.child_roles:
                    hierarchy.append(child)
                    add_children(child)
            
            add_children(role)
            
            return hierarchy
        except Exception as e:
            self.handle_db_error(e, "get role hierarchy")


class PermissionCRUDService(CRUDService[Permission, BaseModel, BaseModel]):
    """CRUD service for Permission model."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(Permission, settings)
    
    def get_by_code(self, code: str) -> Optional[Permission]:
        """Get permission by code."""
        return self.get_by_field("code", code)
    
    def get_by_resource_action(self, resource: str, action: str) -> Optional[Permission]:
        """Get permission by resource and action."""
        try:
            return (
                self.db.query(Permission)
                .filter(Permission.resource == resource)
                .filter(Permission.action == action)
                .first()
            )
        except Exception as e:
            self.handle_db_error(e, "get permission by resource and action")
    
    def get_permissions_by_role(self, role_id: UUID) -> List[Permission]:
        """Get permissions by role."""
        try:
            return (
                self.db.query(Permission)
                .join(RolePermission)
                .filter(RolePermission.role_id == role_id)
                .filter(Permission.is_active == True)
                .all()
            )
        except Exception as e:
            self.handle_db_error(e, "get permissions by role")
    
    def get_permissions_by_group(self, group_id: UUID) -> List[Permission]:
        """Get permissions by group."""
        try:
            return (
                self.db.query(Permission)
                .join(Permission.groups)
                .filter(PermissionGroup.id == group_id)
                .filter(Permission.is_active == True)
                .all()
            )
        except Exception as e:
            self.handle_db_error(e, "get permissions by group")


class PermissionGroupCRUDService(CRUDService[PermissionGroup, BaseModel, BaseModel]):
    """CRUD service for PermissionGroup model."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(PermissionGroup, settings)
    
    def get_by_code(self, code: str) -> Optional[PermissionGroup]:
        """Get permission group by code."""
        return self.get_by_field("code", code)


class ApplicationCRUDService(CRUDService[Application, BaseModel, BaseModel]):
    """CRUD service for Application model."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(Application, settings)
    
    def get_by_code(self, code: str) -> Optional[Application]:
        """Get application by code."""
        return self.get_by_field("code", code)
    
    def get_active_applications(self, skip: int = 0, limit: int = 100) -> List[Application]:
        """Get active applications."""
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"status": "active", "is_deleted": False}
        )
    
    def get_applications_by_type(self, app_type: str) -> List[Application]:
        """Get applications by type."""
        return self.get_multi(filters={"type": app_type})


class ApplicationModuleCRUDService(CRUDService[ApplicationModule, BaseModel, BaseModel]):
    """CRUD service for ApplicationModule model."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(ApplicationModule, settings)
    
    def get_by_application(self, application_id: UUID) -> List[ApplicationModule]:
        """Get modules by application."""
        return self.get_multi(filters={"application_id": application_id})
    
    def get_active_modules(self, application_id: UUID) -> List[ApplicationModule]:
        """Get active modules by application."""
        return self.get_multi(
            filters={
                "application_id": application_id,
                "status": "active",
                "is_enabled": True
            }
        )


class ApplicationConfigCRUDService(CRUDService[ApplicationConfig, BaseModel, BaseModel]):
    """CRUD service for ApplicationConfig model."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(ApplicationConfig, settings)
    
    def get_by_application(self, application_id: UUID) -> List[ApplicationConfig]:
        """Get configs by application."""
        return self.get_multi(filters={"application_id": application_id})
    
    def get_config_value(self, application_id: UUID, key: str) -> Optional[str]:
        """Get config value by key."""
        try:
            config = (
                self.db.query(ApplicationConfig)
                .filter(ApplicationConfig.application_id == application_id)
                .filter(ApplicationConfig.key == key)
                .first()
            )
            return config.value if config else None
        except Exception as e:
            self.handle_db_error(e, "get config value")


class AuditLogCRUDService(CRUDService[AuditLog, BaseModel, BaseModel]):
    """CRUD service for AuditLog model."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(AuditLog, settings)
    
    def get_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by user."""
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"user_id": user_id},
            order_by="timestamp",
            order_desc=True
        )
    
    def get_by_resource(self, resource_type: str, resource_id: str) -> List[AuditLog]:
        """Get audit logs by resource."""
        return self.get_multi(
            filters={"resource_type": resource_type, "resource_id": resource_id},
            order_by="timestamp",
            order_desc=True
        )
    
    def get_by_action(self, action: str, skip: int = 0, limit: int = 100) -> List[AuditLog]:
        """Get audit logs by action."""
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"action": action},
            order_by="timestamp",
            order_desc=True
        )


class UserSessionCRUDService(CRUDService[UserSession, BaseModel, BaseModel]):
    """CRUD service for UserSession model."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(UserSession, settings)
    
    def get_by_token(self, token: str) -> Optional[UserSession]:
        """Get session by token."""
        return self.get_by_field("token", token)
    
    def get_active_sessions(self, user_id: UUID) -> List[UserSession]:
        """Get active sessions for user."""
        return self.get_multi(
            filters={
                "user_id": user_id,
                "status": "active",
                "is_active": True
            },
            order_by="last_activity_at",
            order_desc=True
        )
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        try:
            current_time = datetime.utcnow()
            result = (
                self.db.query(UserSession)
                .filter(UserSession.expires_at < current_time)
                .filter(UserSession.status == "active")
                .update({"status": "expired", "is_active": False})
            )
            self.db.commit()
            return result
        except Exception as e:
            self.db.rollback()
            self.handle_db_error(e, "cleanup expired sessions")


class NotificationCRUDService(CRUDService[Notification, BaseModel, BaseModel]):
    """CRUD service for Notification model."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(Notification, settings)
    
    def get_pending_notifications(self, skip: int = 0, limit: int = 100) -> List[Notification]:
        """Get pending notifications."""
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"status": "pending"},
            order_by="scheduled_at"
        )
    
    def get_notifications_by_user(self, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Notification]:
        """Get notifications for user."""
        try:
            return (
                self.db.query(Notification)
                .join(UserNotification)
                .filter(UserNotification.user_id == user_id)
                .order_by(Notification.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            self.handle_db_error(e, "get notifications by user")


class FileCRUDService(CRUDService[File, BaseModel, BaseModel]):
    """CRUD service for File model."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(File, settings)
    
    def get_by_hash(self, file_hash: str) -> Optional[File]:
        """Get file by hash."""
        return self.get_by_field("file_hash", file_hash)
    
    def get_by_owner(self, owner_id: UUID, skip: int = 0, limit: int = 100) -> List[File]:
        """Get files by owner."""
        return self.get_multi(
            skip=skip,
            limit=limit,
            filters={"owner_id": owner_id, "status": "active"},
            order_by="created_at",
            order_desc=True
        )
    
    def search_files(
        self,
        search_term: str,
        owner_id: UUID = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        """Search files by name or description."""
        try:
            query = self.db.query(File)
            
            # Add search conditions
            search_conditions = [
                File.filename.ilike(f"%{search_term}%"),
                File.description.ilike(f"%{search_term}%")
            ]
            query = query.filter(or_(*search_conditions))
            
            # Filter by owner if specified
            if owner_id:
                query = query.filter(File.owner_id == owner_id)
            
            # Filter active files
            query = query.filter(File.status == "active")
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            self.handle_db_error(e, "search files")