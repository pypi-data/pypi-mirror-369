"""Session models for managing user sessions and authentication."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from enum import Enum

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship

from ..database.base import BaseModel
from ..database.mixins import TimestampMixin


class SessionStatus(str, Enum):
    """Session status enumeration."""
    ACTIVE = "active"
    EXPIRED = "expired"
    TERMINATED = "terminated"
    SUSPENDED = "suspended"
    INVALID = "invalid"


class SessionType(str, Enum):
    """Session type enumeration."""
    WEB = "web"
    API = "api"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    SERVICE = "service"
    ADMIN = "admin"
    TEMPORARY = "temporary"


class DeviceType(str, Enum):
    """Device type enumeration."""
    DESKTOP = "desktop"
    MOBILE = "mobile"
    TABLET = "tablet"
    TV = "tv"
    WATCH = "watch"
    IOT = "iot"
    UNKNOWN = "unknown"


class UserSession(BaseModel, TimestampMixin):
    """User session model for managing authentication sessions."""
    
    __tablename__ = "user_session"
    
    # User reference
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=False,
        index=True,
        comment="User ID"
    )
    
    # Session identification
    session_token = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Unique session token"
    )
    
    refresh_token = Column(
        String(255),
        unique=True,
        nullable=True,
        index=True,
        comment="Refresh token for session renewal"
    )
    
    # Session properties
    session_type = Column(
        String(20),
        default=SessionType.WEB,
        nullable=False,
        comment="Session type"
    )
    
    status = Column(
        String(20),
        default=SessionStatus.ACTIVE,
        nullable=False,
        index=True,
        comment="Session status"
    )
    
    # Time management
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Session expiration time"
    )
    
    last_activity = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last activity timestamp"
    )
    
    # Client information
    ip_address = Column(
        INET,
        nullable=True,
        comment="Client IP address"
    )
    
    user_agent = Column(
        Text,
        nullable=True,
        comment="Client user agent"
    )
    
    device_type = Column(
        String(20),
        default=DeviceType.UNKNOWN,
        nullable=False,
        comment="Device type"
    )
    
    device_id = Column(
        String(255),
        nullable=True,
        comment="Device identifier"
    )
    
    device_name = Column(
        String(200),
        nullable=True,
        comment="Device name"
    )
    
    # Location information
    location_country = Column(
        String(100),
        nullable=True,
        comment="Country from IP geolocation"
    )
    
    location_city = Column(
        String(100),
        nullable=True,
        comment="City from IP geolocation"
    )
    
    location_coordinates = Column(
        JSONB,
        nullable=True,
        comment="GPS coordinates if available"
    )
    
    # Application context
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("application.id"),
        nullable=True,
        comment="Application ID"
    )
    
    # Security features
    is_secure = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Session uses secure connection"
    )
    
    is_remember_me = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Remember me session"
    )
    
    two_factor_verified = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Two-factor authentication verified"
    )
    
    # Session data
    session_data = Column(
        JSONB,
        nullable=True,
        comment="Session-specific data"
    )
    
    # Termination information
    terminated_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Session termination time"
    )
    
    termination_reason = Column(
        String(100),
        nullable=True,
        comment="Reason for session termination"
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="sessions"
    )
    
    application = relationship(
        "Application"
    )
    
    activities = relationship(
        "SessionActivity",
        back_populates="session",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<UserSession(id={self.id}, user_id={self.user_id}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if session is active."""
        return (
            self.status == SessionStatus.ACTIVE and
            self.expires_at > datetime.utcnow()
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if session is expired."""
        return self.expires_at <= datetime.utcnow()
    
    @property
    def time_until_expiry(self) -> timedelta:
        """Get time until session expires."""
        return self.expires_at - datetime.utcnow()
    
    @property
    def duration(self) -> timedelta:
        """Get session duration."""
        end_time = self.terminated_at or datetime.utcnow()
        return end_time - self.created_at
    
    @property
    def idle_time(self) -> timedelta:
        """Get idle time since last activity."""
        if self.last_activity:
            return datetime.utcnow() - self.last_activity
        return datetime.utcnow() - self.created_at
    
    def extend_session(self, duration: timedelta = None) -> None:
        """Extend session expiration time."""
        if duration is None:
            # Default extension of 1 hour
            duration = timedelta(hours=1)
        
        self.expires_at = datetime.utcnow() + duration
        self.update_activity()
    
    def update_activity(self, activity_time: datetime = None) -> None:
        """Update last activity time."""
        self.last_activity = activity_time or datetime.utcnow()
    
    def terminate(self, reason: str = None) -> None:
        """Terminate the session."""
        self.status = SessionStatus.TERMINATED
        self.terminated_at = datetime.utcnow()
        if reason:
            self.termination_reason = reason
    
    def suspend(self, reason: str = None) -> None:
        """Suspend the session."""
        self.status = SessionStatus.SUSPENDED
        if reason:
            self.termination_reason = reason
    
    def reactivate(self) -> None:
        """Reactivate suspended session."""
        if self.status == SessionStatus.SUSPENDED and not self.is_expired:
            self.status = SessionStatus.ACTIVE
            self.termination_reason = None
            self.update_activity()
    
    def invalidate(self, reason: str = None) -> None:
        """Invalidate the session."""
        self.status = SessionStatus.INVALID
        self.terminated_at = datetime.utcnow()
        if reason:
            self.termination_reason = reason
    
    def get_session_data(self, key: str, default=None):
        """Get session data value."""
        if self.session_data and key in self.session_data:
            return self.session_data[key]
        return default
    
    def set_session_data(self, key: str, value: Any) -> None:
        """Set session data value."""
        if self.session_data is None:
            self.session_data = {}
        self.session_data[key] = value
    
    def remove_session_data(self, key: str) -> None:
        """Remove session data key."""
        if self.session_data and key in self.session_data:
            del self.session_data[key]
    
    def clear_session_data(self) -> None:
        """Clear all session data."""
        self.session_data = None
    
    def add_activity(self, activity_type: str, description: str = None, metadata: Dict[str, Any] = None) -> 'SessionActivity':
        """Add session activity record."""
        activity = SessionActivity(
            session_id=self.id,
            activity_type=activity_type,
            description=description,
            metadata=metadata
        )
        self.activities.append(activity)
        self.update_activity()
        return activity
    
    @classmethod
    def create_session(
        cls,
        user_id: str,
        session_token: str,
        expires_in: timedelta = None,
        session_type: SessionType = SessionType.WEB,
        **kwargs
    ) -> 'UserSession':
        """Create new user session."""
        if expires_in is None:
            expires_in = timedelta(hours=24)  # Default 24 hours
        
        return cls(
            user_id=user_id,
            session_token=session_token,
            session_type=session_type,
            expires_at=datetime.utcnow() + expires_in,
            last_activity=datetime.utcnow(),
            **kwargs
        )


class SessionActivity(BaseModel, TimestampMixin):
    """Session activity model for tracking user activities within a session."""
    
    __tablename__ = "session_activity"
    
    # Session reference
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_session.id"),
        nullable=False,
        index=True,
        comment="Session ID"
    )
    
    # Activity information
    activity_type = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Type of activity"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Activity description"
    )
    
    # Request information
    endpoint = Column(
        String(500),
        nullable=True,
        comment="API endpoint or URL"
    )
    
    method = Column(
        String(10),
        nullable=True,
        comment="HTTP method"
    )
    
    status_code = Column(
        Integer,
        nullable=True,
        comment="HTTP status code"
    )
    
    # Performance metrics
    duration_ms = Column(
        Integer,
        nullable=True,
        comment="Activity duration in milliseconds"
    )
    
    # Additional data
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional activity metadata"
    )
    
    # Relationships
    session = relationship(
        "UserSession",
        back_populates="activities"
    )
    
    def __repr__(self) -> str:
        return f"<SessionActivity(id={self.id}, type={self.activity_type}, session_id={self.session_id})>"
    
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


class RefreshToken(BaseModel, TimestampMixin):
    """Refresh token model for managing token refresh."""
    
    __tablename__ = "refresh_token"
    
    # User and session references
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=False,
        index=True,
        comment="User ID"
    )
    
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user_session.id"),
        nullable=True,
        comment="Associated session ID"
    )
    
    # Token information
    token = Column(
        String(255),
        unique=True,
        nullable=False,
        index=True,
        comment="Refresh token"
    )
    
    token_hash = Column(
        String(255),
        nullable=True,
        comment="Hashed token for security"
    )
    
    # Token properties
    expires_at = Column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
        comment="Token expiration time"
    )
    
    is_revoked = Column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
        comment="Token is revoked"
    )
    
    revoked_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Token revocation time"
    )
    
    revocation_reason = Column(
        String(100),
        nullable=True,
        comment="Reason for token revocation"
    )
    
    # Usage tracking
    used_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of times token was used"
    )
    
    last_used_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last usage timestamp"
    )
    
    # Client information
    client_id = Column(
        String(255),
        nullable=True,
        comment="Client identifier"
    )
    
    # Relationships
    user = relationship(
        "User"
    )
    
    session = relationship(
        "UserSession"
    )
    
    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, revoked={self.is_revoked})>"
    
    @property
    def is_valid(self) -> bool:
        """Check if refresh token is valid."""
        return (
            not self.is_revoked and
            self.expires_at > datetime.utcnow()
        )
    
    @property
    def is_expired(self) -> bool:
        """Check if refresh token is expired."""
        return self.expires_at <= datetime.utcnow()
    
    def use_token(self) -> None:
        """Mark token as used."""
        self.used_count += 1
        self.last_used_at = datetime.utcnow()
    
    def revoke(self, reason: str = None) -> None:
        """Revoke the refresh token."""
        self.is_revoked = True
        self.revoked_at = datetime.utcnow()
        if reason:
            self.revocation_reason = reason
    
    @classmethod
    def create_token(
        cls,
        user_id: str,
        token: str,
        expires_in: timedelta = None,
        session_id: str = None,
        **kwargs
    ) -> 'RefreshToken':
        """Create new refresh token."""
        if expires_in is None:
            expires_in = timedelta(days=30)  # Default 30 days
        
        return cls(
            user_id=user_id,
            session_id=session_id,
            token=token,
            expires_at=datetime.utcnow() + expires_in,
            **kwargs
        )