"""User management services."""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from pydantic import BaseModel, EmailStr

from .base import BaseService, ServiceException, NotFoundError, ValidationException, DuplicateError
from .crud import UserCRUDService, UserProfileCRUDService, UserPreferenceCRUDService, RoleCRUDService
from .auth import PasswordService
from ..models.user import User, UserProfile, UserPreference
from ..models.role import Role
from ..config import CoreSettings


class UserCreateSchema(BaseModel):
    """Schema for creating a user."""
    username: str
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: bool = True
    force_password_change: bool = False
    role_ids: Optional[List[UUID]] = None


class UserUpdateSchema(BaseModel):
    """Schema for updating a user."""
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
    is_locked: Optional[bool] = None
    force_password_change: Optional[bool] = None
    role_ids: Optional[List[UUID]] = None


class UserProfileCreateSchema(BaseModel):
    """Schema for creating a user profile."""
    user_id: UUID
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None


class UserProfileUpdateSchema(BaseModel):
    """Schema for updating a user profile."""
    phone: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
    postal_code: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    bio: Optional[str] = None
    website: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    department: Optional[str] = None
    avatar_url: Optional[str] = None


class UserPreferenceCreateSchema(BaseModel):
    """Schema for creating user preferences."""
    user_id: UUID
    language: str = "en"
    timezone: str = "UTC"
    theme: str = "light"
    date_format: str = "YYYY-MM-DD"
    time_format: str = "24h"
    email_notifications: bool = True
    push_notifications: bool = True
    sms_notifications: bool = False
    privacy_profile_visible: bool = True
    privacy_email_visible: bool = False
    privacy_phone_visible: bool = False


class UserPreferenceUpdateSchema(BaseModel):
    """Schema for updating user preferences."""
    language: Optional[str] = None
    timezone: Optional[str] = None
    theme: Optional[str] = None
    date_format: Optional[str] = None
    time_format: Optional[str] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    sms_notifications: Optional[bool] = None
    privacy_profile_visible: Optional[bool] = None
    privacy_email_visible: Optional[bool] = None
    privacy_phone_visible: Optional[bool] = None


class UserService(BaseService):
    """Service for user management."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        self.user_crud = UserCRUDService(settings)
        self.profile_crud = UserProfileCRUDService(settings)
        self.preference_crud = UserPreferenceCRUDService(settings)
        self.role_crud = RoleCRUDService(settings)
        self.password_service = PasswordService(settings)
    
    def create_user(self, user_data: UserCreateSchema) -> User:
        """Create a new user."""
        try:
            # Validate input
            user_data = self.validate_input(user_data, UserCreateSchema)
            
            # Check if username already exists
            existing_user = self.user_crud.get_by_username(user_data.username)
            if existing_user:
                raise DuplicateError("User", "username", user_data.username)
            
            # Check if email already exists
            existing_user = self.user_crud.get_by_email(user_data.email)
            if existing_user:
                raise DuplicateError("User", "email", user_data.email)
            
            # Validate password
            password_validation = self.password_service.validate_password_strength(user_data.password)
            if not password_validation["is_valid"]:
                raise ValidationException(
                    "Password does not meet requirements",
                    details=password_validation
                )
            
            # Hash password
            password_hash = self.password_service.hash_password(user_data.password)
            
            # Create user data
            create_data = {
                "id": uuid4(),
                "username": user_data.username,
                "email": user_data.email,
                "password_hash": password_hash,
                "first_name": user_data.first_name,
                "last_name": user_data.last_name,
                "is_active": user_data.is_active,
                "force_password_change": user_data.force_password_change,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create user
            user = self.user_crud.create(create_data, commit=False)
            
            # Assign roles if provided
            if user_data.role_ids:
                roles = []
                for role_id in user_data.role_ids:
                    role = self.role_crud.get(role_id)
                    if role and role.is_active and not role.is_deleted:
                        roles.append(role)
                user.roles = roles
            
            # Commit transaction
            self.db.commit()
            self.db.refresh(user)
            
            self.log_operation("create_user", {
                "user_id": user.id,
                "username": user.username,
                "email": user.email
            })
            
            return user
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create user")
    
    def get_user(self, user_id: UUID, include_profile: bool = False, include_preferences: bool = False) -> Optional[User]:
        """Get a user by ID with optional profile and preferences."""
        try:
            user = self.user_crud.get(user_id)
            if not user:
                return None
            
            # Load profile if requested
            if include_profile:
                user.profile = self.profile_crud.get_by_user_id(user_id)
            
            # Load preferences if requested
            if include_preferences:
                user.preferences = self.preference_crud.get_by_user_id(user_id)
            
            return user
        except Exception as e:
            self.handle_db_error(e, "get user")
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by username."""
        return self.user_crud.get_by_username(username)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get a user by email."""
        return self.user_crud.get_by_email(email)
    
    def update_user(self, user_id: UUID, user_data: UserUpdateSchema) -> User:
        """Update a user."""
        try:
            # Validate input
            user_data = self.validate_input(user_data, UserUpdateSchema)
            
            # Get existing user
            user = self.user_crud.get(user_id)
            if not user:
                raise NotFoundError("User", user_id)
            
            # Check for username conflicts
            if user_data.username and user_data.username != user.username:
                existing_user = self.user_crud.get_by_username(user_data.username)
                if existing_user and existing_user.id != user_id:
                    raise DuplicateError("User", "username", user_data.username)
            
            # Check for email conflicts
            if user_data.email and user_data.email != user.email:
                existing_user = self.user_crud.get_by_email(user_data.email)
                if existing_user and existing_user.id != user_id:
                    raise DuplicateError("User", "email", user_data.email)
            
            # Update user data
            update_data = user_data.dict(exclude_unset=True, exclude={"role_ids"})
            
            # Update roles if provided
            if user_data.role_ids is not None:
                roles = []
                for role_id in user_data.role_ids:
                    role = self.role_crud.get(role_id)
                    if role and role.is_active and not role.is_deleted:
                        roles.append(role)
                user.roles = roles
            
            # Update user
            updated_user = self.user_crud.update(user_id, update_data)
            
            self.log_operation("update_user", {
                "user_id": user_id,
                "updated_fields": list(update_data.keys())
            })
            
            return updated_user
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "update user")
    
    def delete_user(self, user_id: UUID, soft_delete: bool = True) -> bool:
        """Delete a user."""
        try:
            user = self.user_crud.get(user_id)
            if not user:
                raise NotFoundError("User", user_id)
            
            # Perform deletion
            result = self.user_crud.delete(user_id, soft_delete=soft_delete)
            
            self.log_operation("delete_user", {
                "user_id": user_id,
                "soft_delete": soft_delete
            })
            
            return result
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "delete user")
    
    def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        search: str = None,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> List[User]:
        """List users with filtering and pagination."""
        try:
            if search:
                return self.user_crud.search_users(search, skip, limit)
            else:
                return self.user_crud.get_multi(
                    skip=skip,
                    limit=limit,
                    filters=filters,
                    order_by=order_by,
                    order_desc=order_desc
                )
        except Exception as e:
            self.handle_db_error(e, "list users")
    
    def count_users(self, filters: Dict[str, Any] = None) -> int:
        """Count users with optional filtering."""
        return self.user_crud.count(filters)
    
    def activate_user(self, user_id: UUID) -> User:
        """Activate a user account."""
        return self.update_user(user_id, UserUpdateSchema(is_active=True))
    
    def deactivate_user(self, user_id: UUID) -> User:
        """Deactivate a user account."""
        return self.update_user(user_id, UserUpdateSchema(is_active=False))
    
    def lock_user(self, user_id: UUID, duration_minutes: int = None) -> User:
        """Lock a user account."""
        update_data = {"is_locked": True}
        
        if duration_minutes:
            update_data["locked_until"] = datetime.utcnow() + timedelta(minutes=duration_minutes)
        
        return self.update_user(user_id, UserUpdateSchema(**update_data))
    
    def unlock_user(self, user_id: UUID) -> User:
        """Unlock a user account."""
        return self.update_user(user_id, UserUpdateSchema(
            is_locked=False,
            locked_until=None,
            failed_login_attempts=0
        ))
    
    def assign_roles(self, user_id: UUID, role_ids: List[UUID]) -> User:
        """Assign roles to a user."""
        return self.update_user(user_id, UserUpdateSchema(role_ids=role_ids))
    
    def add_role(self, user_id: UUID, role_id: UUID) -> User:
        """Add a role to a user."""
        try:
            user = self.user_crud.get(user_id)
            if not user:
                raise NotFoundError("User", user_id)
            
            role = self.role_crud.get(role_id)
            if not role:
                raise NotFoundError("Role", role_id)
            
            if role not in user.roles:
                user.roles.append(role)
                self.db.commit()
                self.db.refresh(user)
            
            self.log_operation("add_role", {
                "user_id": user_id,
                "role_id": role_id
            })
            
            return user
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "add role")
    
    def remove_role(self, user_id: UUID, role_id: UUID) -> User:
        """Remove a role from a user."""
        try:
            user = self.user_crud.get(user_id)
            if not user:
                raise NotFoundError("User", user_id)
            
            role = self.role_crud.get(role_id)
            if not role:
                raise NotFoundError("Role", role_id)
            
            if role in user.roles:
                user.roles.remove(role)
                self.db.commit()
                self.db.refresh(user)
            
            self.log_operation("remove_role", {
                "user_id": user_id,
                "role_id": role_id
            })
            
            return user
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "remove role")
    
    def get_users_by_role(self, role_id: UUID, skip: int = 0, limit: int = 100) -> List[User]:
        """Get users by role."""
        return self.user_crud.get_users_by_role(role_id, skip, limit)


class UserProfileService(BaseService):
    """Service for user profile management."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        self.profile_crud = UserProfileCRUDService(settings)
        self.user_crud = UserCRUDService(settings)
    
    def create_profile(self, profile_data: UserProfileCreateSchema) -> UserProfile:
        """Create a user profile."""
        try:
            # Validate input
            profile_data = self.validate_input(profile_data, UserProfileCreateSchema)
            
            # Check if user exists
            user = self.user_crud.get(profile_data.user_id)
            if not user:
                raise NotFoundError("User", profile_data.user_id)
            
            # Check if profile already exists
            existing_profile = self.profile_crud.get_by_user_id(profile_data.user_id)
            if existing_profile:
                raise DuplicateError("UserProfile", "user_id", profile_data.user_id)
            
            # Create profile
            create_data = profile_data.dict()
            create_data["id"] = uuid4()
            
            profile = self.profile_crud.create(create_data)
            
            self.log_operation("create_profile", {
                "user_id": profile_data.user_id,
                "profile_id": profile.id
            })
            
            return profile
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create profile")
    
    def get_profile(self, user_id: UUID) -> Optional[UserProfile]:
        """Get user profile by user ID."""
        return self.profile_crud.get_by_user_id(user_id)
    
    def update_profile(self, user_id: UUID, profile_data: UserProfileUpdateSchema) -> UserProfile:
        """Update user profile."""
        try:
            # Validate input
            profile_data = self.validate_input(profile_data, UserProfileUpdateSchema)
            
            # Get existing profile
            profile = self.profile_crud.get_by_user_id(user_id)
            if not profile:
                raise NotFoundError("UserProfile", f"user_id={user_id}")
            
            # Update profile
            update_data = profile_data.dict(exclude_unset=True)
            updated_profile = self.profile_crud.update(profile.id, update_data)
            
            self.log_operation("update_profile", {
                "user_id": user_id,
                "profile_id": profile.id,
                "updated_fields": list(update_data.keys())
            })
            
            return updated_profile
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "update profile")
    
    def delete_profile(self, user_id: UUID) -> bool:
        """Delete user profile."""
        try:
            profile = self.profile_crud.get_by_user_id(user_id)
            if not profile:
                raise NotFoundError("UserProfile", f"user_id={user_id}")
            
            result = self.profile_crud.delete(profile.id)
            
            self.log_operation("delete_profile", {
                "user_id": user_id,
                "profile_id": profile.id
            })
            
            return result
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "delete profile")


class UserPreferenceService(BaseService):
    """Service for user preference management."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        self.preference_crud = UserPreferenceCRUDService(settings)
        self.user_crud = UserCRUDService(settings)
    
    def create_preferences(self, preference_data: UserPreferenceCreateSchema) -> UserPreference:
        """Create user preferences."""
        try:
            # Validate input
            preference_data = self.validate_input(preference_data, UserPreferenceCreateSchema)
            
            # Check if user exists
            user = self.user_crud.get(preference_data.user_id)
            if not user:
                raise NotFoundError("User", preference_data.user_id)
            
            # Check if preferences already exist
            existing_preferences = self.preference_crud.get_by_user_id(preference_data.user_id)
            if existing_preferences:
                raise DuplicateError("UserPreference", "user_id", preference_data.user_id)
            
            # Create preferences
            create_data = preference_data.dict()
            create_data["id"] = uuid4()
            
            preferences = self.preference_crud.create(create_data)
            
            self.log_operation("create_preferences", {
                "user_id": preference_data.user_id,
                "preferences_id": preferences.id
            })
            
            return preferences
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create preferences")
    
    def get_preferences(self, user_id: UUID) -> Optional[UserPreference]:
        """Get user preferences by user ID."""
        return self.preference_crud.get_by_user_id(user_id)
    
    def update_preferences(self, user_id: UUID, preference_data: UserPreferenceUpdateSchema) -> UserPreference:
        """Update user preferences."""
        try:
            # Validate input
            preference_data = self.validate_input(preference_data, UserPreferenceUpdateSchema)
            
            # Get existing preferences
            preferences = self.preference_crud.get_by_user_id(user_id)
            if not preferences:
                raise NotFoundError("UserPreference", f"user_id={user_id}")
            
            # Update preferences
            update_data = preference_data.dict(exclude_unset=True)
            updated_preferences = self.preference_crud.update(preferences.id, update_data)
            
            self.log_operation("update_preferences", {
                "user_id": user_id,
                "preferences_id": preferences.id,
                "updated_fields": list(update_data.keys())
            })
            
            return updated_preferences
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "update preferences")
    
    def get_or_create_preferences(self, user_id: UUID) -> UserPreference:
        """Get user preferences or create default ones if they don't exist."""
        preferences = self.get_preferences(user_id)
        
        if not preferences:
            # Create default preferences
            default_data = UserPreferenceCreateSchema(user_id=user_id)
            preferences = self.create_preferences(default_data)
        
        return preferences