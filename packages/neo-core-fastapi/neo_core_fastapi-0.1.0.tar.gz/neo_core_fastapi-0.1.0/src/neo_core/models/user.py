"""User models for authentication and user management."""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ..database.base import BaseModel
from ..database.mixins import TimestampMixin, SoftDeleteMixin, AuditMixin


class UserStatus(str, Enum):
    """User status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING = "pending"
    BANNED = "banned"


class UserType(str, Enum):
    """User type enumeration."""
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"
    SERVICE = "service"
    SYSTEM = "system"


# Association table for user roles (many-to-many)
user_roles = Table(
    'user_roles',
    BaseModel.metadata,
    Column('user_id', UUID(as_uuid=True), ForeignKey('user.id'), primary_key=True),
    Column('role_id', UUID(as_uuid=True), ForeignKey('role.id'), primary_key=True),
    Column('assigned_at', DateTime(timezone=True), default=datetime.utcnow),
    Column('assigned_by', UUID(as_uuid=True), nullable=True),
    Column('expires_at', DateTime(timezone=True), nullable=True),
)


class User(BaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """User model for authentication and authorization."""
    
    __tablename__ = "user"
    
    # Basic information
    username = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique username"
    )
    
    email = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="User email address"
    )
    
    phone = Column(
        String(20),
        nullable=True,
        index=True,
        comment="User phone number"
    )
    
    # Authentication
    password_hash = Column(
        String(255),
        nullable=False,
        comment="Hashed password"
    )
    
    salt = Column(
        String(255),
        nullable=True,
        comment="Password salt"
    )
    
    # Status and type
    status = Column(
        String(20),
        default=UserStatus.PENDING,
        nullable=False,
        comment="User status"
    )
    
    user_type = Column(
        String(20),
        default=UserType.USER,
        nullable=False,
        comment="User type"
    )
    
    # Security
    is_email_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Email verification status"
    )
    
    is_phone_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Phone verification status"
    )
    
    is_two_factor_enabled = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Two-factor authentication status"
    )
    
    two_factor_secret = Column(
        String(255),
        nullable=True,
        comment="Two-factor authentication secret"
    )
    
    # Login tracking
    last_login_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last login timestamp"
    )
    
    last_login_ip = Column(
        String(45),
        nullable=True,
        comment="Last login IP address"
    )
    
    login_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Total login count"
    )
    
    failed_login_attempts = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Failed login attempts"
    )
    
    locked_until = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Account lock expiration"
    )
    
    # Password management
    password_changed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last password change timestamp"
    )
    
    password_reset_token = Column(
        String(255),
        nullable=True,
        comment="Password reset token"
    )
    
    password_reset_expires = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Password reset token expiration"
    )
    
    # Email verification
    email_verification_token = Column(
        String(255),
        nullable=True,
        comment="Email verification token"
    )
    
    email_verification_expires = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Email verification token expiration"
    )
    
    # Relationships
    profile = relationship(
        "UserProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    preferences = relationship(
        "UserPreference",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan"
    )
    
    roles = relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="dynamic"
    )
    
    sessions = relationship(
        "UserSession",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    audit_logs = relationship(
        "AuditLog",
        foreign_keys="AuditLog.user_id",
        back_populates="user"
    )
    
    notifications = relationship(
        "Notification",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email})>"
    
    @property
    def is_active(self) -> bool:
        """Check if user is active."""
        return self.status == UserStatus.ACTIVE and not self.is_deleted
    
    @property
    def is_locked(self) -> bool:
        """Check if user account is locked."""
        if self.locked_until:
            return datetime.utcnow() < self.locked_until
        return False
    
    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.user_type == UserType.ADMIN
    
    @property
    def full_name(self) -> str:
        """Get user's full name from profile."""
        if self.profile:
            return f"{self.profile.first_name} {self.profile.last_name}".strip()
        return self.username
    
    def activate(self) -> None:
        """Activate user account."""
        self.status = UserStatus.ACTIVE
        self.failed_login_attempts = 0
        self.locked_until = None
    
    def deactivate(self) -> None:
        """Deactivate user account."""
        self.status = UserStatus.INACTIVE
    
    def suspend(self, reason: Optional[str] = None) -> None:
        """Suspend user account."""
        self.status = UserStatus.SUSPENDED
        # Could store reason in audit log
    
    def ban(self, reason: Optional[str] = None) -> None:
        """Ban user account."""
        self.status = UserStatus.BANNED
        # Could store reason in audit log
    
    def lock_account(self, duration_minutes: int = 30) -> None:
        """Lock user account for specified duration."""
        from datetime import timedelta
        self.locked_until = datetime.utcnow() + timedelta(minutes=duration_minutes)
    
    def unlock_account(self) -> None:
        """Unlock user account."""
        self.locked_until = None
        self.failed_login_attempts = 0
    
    def record_login(self, ip_address: Optional[str] = None) -> None:
        """Record successful login."""
        self.last_login_at = datetime.utcnow()
        self.last_login_ip = ip_address
        self.login_count += 1
        self.failed_login_attempts = 0
    
    def record_failed_login(self) -> None:
        """Record failed login attempt."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.lock_account(30)  # Lock for 30 minutes
    
    def has_role(self, role_name: str) -> bool:
        """Check if user has specific role."""
        return any(role.name == role_name for role in self.roles)
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if user has specific permission."""
        for role in self.roles:
            if role.has_permission(permission_name):
                return True
        return False


class UserProfile(BaseModel, TimestampMixin):
    """User profile model for additional user information."""
    
    __tablename__ = "user_profile"
    
    # Foreign key
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=False,
        unique=True,
        comment="User ID"
    )
    
    # Personal information
    first_name = Column(
        String(50),
        nullable=True,
        comment="First name"
    )
    
    last_name = Column(
        String(50),
        nullable=True,
        comment="Last name"
    )
    
    middle_name = Column(
        String(50),
        nullable=True,
        comment="Middle name"
    )
    
    display_name = Column(
        String(100),
        nullable=True,
        comment="Display name"
    )
    
    bio = Column(
        Text,
        nullable=True,
        comment="User biography"
    )
    
    # Contact information
    address = Column(
        Text,
        nullable=True,
        comment="Address"
    )
    
    city = Column(
        String(100),
        nullable=True,
        comment="City"
    )
    
    state = Column(
        String(100),
        nullable=True,
        comment="State/Province"
    )
    
    country = Column(
        String(100),
        nullable=True,
        comment="Country"
    )
    
    postal_code = Column(
        String(20),
        nullable=True,
        comment="Postal code"
    )
    
    # Profile details
    avatar_url = Column(
        String(500),
        nullable=True,
        comment="Avatar image URL"
    )
    
    website = Column(
        String(500),
        nullable=True,
        comment="Personal website"
    )
    
    birth_date = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Birth date"
    )
    
    gender = Column(
        String(20),
        nullable=True,
        comment="Gender"
    )
    
    # Professional information
    job_title = Column(
        String(100),
        nullable=True,
        comment="Job title"
    )
    
    company = Column(
        String(100),
        nullable=True,
        comment="Company name"
    )
    
    department = Column(
        String(100),
        nullable=True,
        comment="Department"
    )
    
    # Social links
    social_links = Column(
        JSONB,
        nullable=True,
        comment="Social media links in JSON format"
    )
    
    # Additional metadata
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional profile metadata"
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="profile"
    )
    
    def __repr__(self) -> str:
        return f"<UserProfile(user_id={self.user_id}, name={self.first_name} {self.last_name})>"
    
    @property
    def full_name(self) -> str:
        """Get full name."""
        parts = [self.first_name, self.middle_name, self.last_name]
        return " ".join(part for part in parts if part)
    
    @property
    def full_address(self) -> str:
        """Get full address."""
        parts = [self.address, self.city, self.state, self.country, self.postal_code]
        return ", ".join(part for part in parts if part)


class UserPreference(BaseModel, TimestampMixin):
    """User preferences model for storing user settings."""
    
    __tablename__ = "user_preference"
    
    # Foreign key
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=False,
        unique=True,
        comment="User ID"
    )
    
    # UI preferences
    theme = Column(
        String(20),
        default="light",
        nullable=False,
        comment="UI theme preference"
    )
    
    language = Column(
        String(10),
        default="en",
        nullable=False,
        comment="Language preference"
    )
    
    timezone = Column(
        String(50),
        default="UTC",
        nullable=False,
        comment="Timezone preference"
    )
    
    date_format = Column(
        String(20),
        default="YYYY-MM-DD",
        nullable=False,
        comment="Date format preference"
    )
    
    time_format = Column(
        String(20),
        default="24h",
        nullable=False,
        comment="Time format preference (12h/24h)"
    )
    
    # Notification preferences
    email_notifications = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Email notifications enabled"
    )
    
    push_notifications = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Push notifications enabled"
    )
    
    sms_notifications = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="SMS notifications enabled"
    )
    
    # Privacy preferences
    profile_visibility = Column(
        String(20),
        default="public",
        nullable=False,
        comment="Profile visibility (public/private/friends)"
    )
    
    show_online_status = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Show online status"
    )
    
    allow_friend_requests = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Allow friend requests"
    )
    
    # Application preferences
    items_per_page = Column(
        Integer,
        default=20,
        nullable=False,
        comment="Items per page in lists"
    )
    
    auto_save = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Auto-save enabled"
    )
    
    # Custom preferences
    custom_settings = Column(
        JSONB,
        nullable=True,
        comment="Custom user settings in JSON format"
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="preferences"
    )
    
    def __repr__(self) -> str:
        return f"<UserPreference(user_id={self.user_id}, theme={self.theme}, language={self.language})>"
    
    def get_custom_setting(self, key: str, default=None):
        """Get custom setting value."""
        if self.custom_settings and isinstance(self.custom_settings, dict):
            return self.custom_settings.get(key, default)
        return default
    
    def set_custom_setting(self, key: str, value) -> None:
        """Set custom setting value."""
        if self.custom_settings is None:
            self.custom_settings = {}
        elif not isinstance(self.custom_settings, dict):
            self.custom_settings = {}
        
        self.custom_settings[key] = value
    
    def remove_custom_setting(self, key: str) -> None:
        """Remove custom setting."""
        if self.custom_settings and isinstance(self.custom_settings, dict):
            self.custom_settings.pop(key, None)