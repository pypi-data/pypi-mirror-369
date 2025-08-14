"""Authentication and authorization services."""

import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Union
from uuid import UUID, uuid4

import bcrypt
import jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from .base import BaseService, ServiceException, NotFoundError, ValidationException, PermissionError
from .crud import UserCRUDService, RoleCRUDService, PermissionCRUDService, UserSessionCRUDService
from ..models.user import User
from ..models.role import Role
from ..models.permission import Permission
from ..models.session import UserSession, SessionStatus, SessionType, DeviceType
from ..config import CoreSettings


class AuthenticationError(ServiceException):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_ERROR")


class AuthorizationError(ServiceException):
    """Exception for authorization errors."""
    
    def __init__(self, message: str = "Authorization failed"):
        super().__init__(message, "AUTHORIZATION_ERROR")


class TokenExpiredError(ServiceException):
    """Exception for expired token errors."""
    
    def __init__(self, message: str = "Token has expired"):
        super().__init__(message, "TOKEN_EXPIRED")


class InvalidTokenError(ServiceException):
    """Exception for invalid token errors."""
    
    def __init__(self, message: str = "Invalid token"):
        super().__init__(message, "INVALID_TOKEN")


class PasswordService:
    """Service for password hashing and verification."""
    
    def __init__(self, settings: CoreSettings = None):
        self.settings = settings or CoreSettings()
        self.pwd_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto",
            bcrypt__rounds=self.settings.password_hash_rounds
        )
    
    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def generate_password(self, length: int = 12) -> str:
        """Generate a random password."""
        import string
        import random
        
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(characters) for _ in range(length))
    
    def validate_password_strength(self, password: str) -> Dict[str, Any]:
        """Validate password strength."""
        result = {
            "is_valid": True,
            "score": 0,
            "issues": []
        }
        
        # Check length
        if len(password) < self.settings.password_min_length:
            result["is_valid"] = False
            result["issues"].append(f"Password must be at least {self.settings.password_min_length} characters")
        else:
            result["score"] += 1
        
        # Check for uppercase
        if not any(c.isupper() for c in password):
            result["issues"].append("Password should contain uppercase letters")
        else:
            result["score"] += 1
        
        # Check for lowercase
        if not any(c.islower() for c in password):
            result["issues"].append("Password should contain lowercase letters")
        else:
            result["score"] += 1
        
        # Check for digits
        if not any(c.isdigit() for c in password):
            result["issues"].append("Password should contain numbers")
        else:
            result["score"] += 1
        
        # Check for special characters
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            result["issues"].append("Password should contain special characters")
        else:
            result["score"] += 1
        
        return result


class TokenService:
    """Service for JWT token management."""
    
    def __init__(self, settings: CoreSettings = None):
        self.settings = settings or CoreSettings()
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create an access token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        
        return jwt.encode(
            to_encode,
            self.settings.secret_key,
            algorithm=self.settings.jwt_algorithm
        )
    
    def create_refresh_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create a refresh token."""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=self.settings.refresh_token_expire_days)
        
        to_encode.update({"exp": expire, "type": "refresh"})
        
        return jwt.encode(
            to_encode,
            self.settings.secret_key,
            algorithm=self.settings.jwt_algorithm
        )
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Verify and decode a token."""
        try:
            payload = jwt.decode(
                token,
                self.settings.secret_key,
                algorithms=[self.settings.jwt_algorithm]
            )
            
            # Check token type
            if payload.get("type") != token_type:
                raise InvalidTokenError(f"Invalid token type. Expected {token_type}")
            
            return payload
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError()
        except jwt.JWTError:
            raise InvalidTokenError()
    
    def generate_session_token(self) -> str:
        """Generate a secure session token."""
        return secrets.token_urlsafe(32)
    
    def generate_api_key(self) -> str:
        """Generate an API key."""
        return secrets.token_urlsafe(40)


class AuthService(BaseService):
    """Main authentication service."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        self.password_service = PasswordService(settings)
        self.token_service = TokenService(settings)
        self.user_service = UserCRUDService(settings)
        self.session_service = UserSessionCRUDService(settings)
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate a user with username/email and password."""
        try:
            # Try to find user by username or email
            user = self.user_service.get_by_username(username)
            if not user:
                user = self.user_service.get_by_email(username)
            
            if not user:
                raise AuthenticationError("User not found")
            
            # Check if user is active
            if not user.is_active:
                raise AuthenticationError("User account is disabled")
            
            # Check if user is deleted
            if user.is_deleted:
                raise AuthenticationError("User account not found")
            
            # Check if account is locked
            if user.is_locked:
                if user.locked_until and user.locked_until > datetime.utcnow():
                    raise AuthenticationError("Account is temporarily locked")
                elif user.locked_until and user.locked_until <= datetime.utcnow():
                    # Unlock account if lock period has expired
                    user.is_locked = False
                    user.locked_until = None
                    user.failed_login_attempts = 0
                    self.db.commit()
                else:
                    raise AuthenticationError("Account is locked")
            
            # Verify password
            if not self.password_service.verify_password(password, user.password_hash):
                # Increment failed login attempts
                user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
                user.last_failed_login_at = datetime.utcnow()
                
                # Lock account if too many failed attempts
                if user.failed_login_attempts >= self.settings.max_login_attempts:
                    user.is_locked = True
                    user.locked_until = datetime.utcnow() + timedelta(
                        minutes=self.settings.account_lockout_duration
                    )
                
                self.db.commit()
                raise AuthenticationError("Invalid password")
            
            # Reset failed login attempts on successful login
            if user.failed_login_attempts > 0:
                user.failed_login_attempts = 0
                user.last_failed_login_at = None
            
            # Update last login
            self.user_service.update_last_login(user.id)
            
            return user
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "authenticate user")
    
    def create_user_session(
        self,
        user: User,
        session_type: SessionType = SessionType.WEB,
        device_info: Dict[str, Any] = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> UserSession:
        """Create a new user session."""
        try:
            # Generate tokens
            session_token = self.token_service.generate_session_token()
            refresh_token = self.token_service.generate_session_token()
            
            # Create session
            session_data = {
                "id": uuid4(),
                "user_id": user.id,
                "token": session_token,
                "refresh_token": refresh_token,
                "type": session_type,
                "status": SessionStatus.ACTIVE,
                "expires_at": datetime.utcnow() + timedelta(
                    minutes=self.settings.session_expire_minutes
                ),
                "last_activity_at": datetime.utcnow(),
                "ip_address": ip_address,
                "user_agent": user_agent,
                "is_active": True
            }
            
            # Add device info if provided
            if device_info:
                session_data.update({
                    "device_type": device_info.get("device_type", DeviceType.UNKNOWN),
                    "device_name": device_info.get("device_name"),
                    "device_id": device_info.get("device_id"),
                    "platform": device_info.get("platform"),
                    "browser": device_info.get("browser")
                })
            
            session = self.session_service.create(session_data)
            
            self.log_operation("create_session", {
                "user_id": user.id,
                "session_id": session.id,
                "session_type": session_type
            })
            
            return session
        except Exception as e:
            self.handle_db_error(e, "create user session")
    
    def verify_session(self, token: str) -> Optional[UserSession]:
        """Verify a session token."""
        try:
            session = self.session_service.get_by_token(token)
            
            if not session:
                return None
            
            # Check if session is active
            if not session.is_active or session.status != SessionStatus.ACTIVE:
                return None
            
            # Check if session has expired
            if session.expires_at and session.expires_at < datetime.utcnow():
                # Mark session as expired
                session.status = SessionStatus.EXPIRED
                session.is_active = False
                self.db.commit()
                return None
            
            # Update last activity
            session.last_activity_at = datetime.utcnow()
            
            # Extend session if needed
            if self.settings.extend_session_on_activity:
                session.expires_at = datetime.utcnow() + timedelta(
                    minutes=self.settings.session_expire_minutes
                )
            
            self.db.commit()
            
            return session
        except Exception as e:
            self.handle_db_error(e, "verify session")
    
    def logout_user(self, token: str) -> bool:
        """Logout a user by invalidating their session."""
        try:
            session = self.session_service.get_by_token(token)
            
            if not session:
                return False
            
            # Mark session as terminated
            session.status = SessionStatus.TERMINATED
            session.is_active = False
            session.terminated_at = datetime.utcnow()
            session.termination_reason = "user_logout"
            
            self.db.commit()
            
            self.log_operation("logout", {
                "user_id": session.user_id,
                "session_id": session.id
            })
            
            return True
        except Exception as e:
            self.handle_db_error(e, "logout user")
    
    def logout_all_sessions(self, user_id: UUID) -> int:
        """Logout all active sessions for a user."""
        try:
            active_sessions = self.session_service.get_active_sessions(user_id)
            
            count = 0
            for session in active_sessions:
                session.status = SessionStatus.TERMINATED
                session.is_active = False
                session.terminated_at = datetime.utcnow()
                session.termination_reason = "logout_all"
                count += 1
            
            self.db.commit()
            
            self.log_operation("logout_all", {
                "user_id": user_id,
                "sessions_terminated": count
            })
            
            return count
        except Exception as e:
            self.handle_db_error(e, "logout all sessions")
    
    def change_password(
        self,
        user_id: UUID,
        current_password: str,
        new_password: str
    ) -> bool:
        """Change user password."""
        try:
            user = self.user_service.get(user_id)
            if not user:
                raise NotFoundError("User", user_id)
            
            # Verify current password
            if not self.password_service.verify_password(current_password, user.password_hash):
                raise AuthenticationError("Current password is incorrect")
            
            # Validate new password
            validation = self.password_service.validate_password_strength(new_password)
            if not validation["is_valid"]:
                raise ValidationException("Password does not meet requirements", details=validation)
            
            # Hash new password
            new_password_hash = self.password_service.hash_password(new_password)
            
            # Update user
            user.password_hash = new_password_hash
            user.password_changed_at = datetime.utcnow()
            
            # Force password change flag off
            if user.force_password_change:
                user.force_password_change = False
            
            self.db.commit()
            
            self.log_operation("change_password", {"user_id": user_id})
            
            return True
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "change password")
    
    def reset_password(self, user_id: UUID, new_password: str = None) -> str:
        """Reset user password (admin function)."""
        try:
            user = self.user_service.get(user_id)
            if not user:
                raise NotFoundError("User", user_id)
            
            # Generate new password if not provided
            if not new_password:
                new_password = self.password_service.generate_password()
            
            # Validate new password
            validation = self.password_service.validate_password_strength(new_password)
            if not validation["is_valid"]:
                raise ValidationException("Generated password does not meet requirements")
            
            # Hash new password
            new_password_hash = self.password_service.hash_password(new_password)
            
            # Update user
            user.password_hash = new_password_hash
            user.password_changed_at = datetime.utcnow()
            user.force_password_change = True
            
            # Reset failed login attempts
            user.failed_login_attempts = 0
            user.last_failed_login_at = None
            
            # Unlock account if locked
            if user.is_locked:
                user.is_locked = False
                user.locked_until = None
            
            self.db.commit()
            
            # Logout all sessions
            self.logout_all_sessions(user_id)
            
            self.log_operation("reset_password", {"user_id": user_id})
            
            return new_password
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "reset password")
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        return self.session_service.cleanup_expired_sessions()


class AuthorizationService(BaseService):
    """Service for handling authorization and permissions."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        self.user_service = UserCRUDService(settings)
        self.role_service = RoleCRUDService(settings)
        self.permission_service = PermissionCRUDService(settings)
    
    def get_user_permissions(self, user_id: UUID) -> List[Permission]:
        """Get all permissions for a user (through roles)."""
        try:
            user = self.user_service.get(user_id)
            if not user:
                raise NotFoundError("User", user_id)
            
            permissions = set()
            
            # Get permissions from user roles
            for role in user.roles:
                if role.is_active and not role.is_deleted:
                    role_permissions = self.permission_service.get_permissions_by_role(role.id)
                    permissions.update(role_permissions)
            
            return list(permissions)
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "get user permissions")
    
    def check_permission(
        self,
        user_id: UUID,
        resource: str,
        action: str,
        context: Dict[str, Any] = None
    ) -> bool:
        """Check if user has permission for a specific resource and action."""
        try:
            permissions = self.get_user_permissions(user_id)
            
            for permission in permissions:
                # Check exact match
                if permission.resource == resource and permission.action == action:
                    # Check conditions if any
                    if permission.conditions:
                        # Simple condition checking (can be extended)
                        if context and self._evaluate_conditions(permission.conditions, context):
                            return True
                    else:
                        return True
                
                # Check wildcard permissions
                if permission.resource == "*" or permission.action == "*":
                    return True
                
                # Check resource hierarchy (e.g., "users.*" matches "users.create")
                if permission.resource.endswith("*"):
                    resource_prefix = permission.resource[:-1]
                    if resource.startswith(resource_prefix):
                        return True
            
            return False
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "check permission")
    
    def require_permission(
        self,
        user_id: UUID,
        resource: str,
        action: str,
        context: Dict[str, Any] = None
    ) -> None:
        """Require permission or raise PermissionError."""
        if not self.check_permission(user_id, resource, action, context):
            raise PermissionError(f"{action} on {resource}")
    
    def check_role(self, user_id: UUID, role_code: str) -> bool:
        """Check if user has a specific role."""
        try:
            user = self.user_service.get(user_id)
            if not user:
                return False
            
            for role in user.roles:
                if role.code == role_code and role.is_active and not role.is_deleted:
                    return True
            
            return False
        except Exception as e:
            self.handle_db_error(e, "check role")
    
    def require_role(self, user_id: UUID, role_code: str) -> None:
        """Require role or raise PermissionError."""
        if not self.check_role(user_id, role_code):
            raise PermissionError(f"Role {role_code} required")
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], context: Dict[str, Any]) -> bool:
        """Evaluate permission conditions against context."""
        # Simple condition evaluation - can be extended
        for key, expected_value in conditions.items():
            if key not in context or context[key] != expected_value:
                return False
        return True