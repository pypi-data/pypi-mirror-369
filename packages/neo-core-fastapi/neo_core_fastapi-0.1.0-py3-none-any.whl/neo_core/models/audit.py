"""Audit models for tracking system operations and changes."""

from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum

from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Boolean, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.orm import relationship

from ..database.base import BaseModel
from ..database.mixins import TimestampMixin


class AuditAction(str, Enum):
    """Audit action enumeration."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    ACCESS = "access"
    EXPORT = "export"
    IMPORT = "import"
    DOWNLOAD = "download"
    UPLOAD = "upload"
    APPROVE = "approve"
    REJECT = "reject"
    ACTIVATE = "activate"
    DEACTIVATE = "deactivate"
    RESET = "reset"
    CHANGE_PASSWORD = "change_password"
    GRANT_PERMISSION = "grant_permission"
    REVOKE_PERMISSION = "revoke_permission"
    ASSIGN_ROLE = "assign_role"
    REMOVE_ROLE = "remove_role"
    CONFIGURE = "configure"
    DEPLOY = "deploy"
    BACKUP = "backup"
    RESTORE = "restore"
    MAINTENANCE = "maintenance"
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"
    DEBUG = "debug"


class AuditLevel(str, Enum):
    """Audit level enumeration."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AuditStatus(str, Enum):
    """Audit status enumeration."""
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    PARTIAL = "partial"
    CANCELLED = "cancelled"


class AuditLog(BaseModel, TimestampMixin):
    """Audit log model for tracking system operations."""
    
    __tablename__ = "audit_log"
    
    # User and session information
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=True,
        index=True,
        comment="User who performed the action"
    )
    
    session_id = Column(
        String(255),
        nullable=True,
        index=True,
        comment="Session ID"
    )
    
    # Action information
    action = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Action performed"
    )
    
    resource_type = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Type of resource affected"
    )
    
    resource_id = Column(
        String(255),
        nullable=True,
        index=True,
        comment="ID of resource affected"
    )
    
    resource_name = Column(
        String(255),
        nullable=True,
        comment="Name of resource affected"
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
    
    # Client information
    ip_address = Column(
        INET,
        nullable=True,
        index=True,
        comment="Client IP address"
    )
    
    user_agent = Column(
        Text,
        nullable=True,
        comment="Client user agent"
    )
    
    # Application context
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("application.id"),
        nullable=True,
        index=True,
        comment="Application ID"
    )
    
    module_name = Column(
        String(100),
        nullable=True,
        comment="Module name"
    )
    
    # Audit metadata
    level = Column(
        String(20),
        default=AuditLevel.INFO,
        nullable=False,
        index=True,
        comment="Audit level"
    )
    
    status = Column(
        String(20),
        default=AuditStatus.SUCCESS,
        nullable=False,
        index=True,
        comment="Operation status"
    )
    
    # Content and details
    message = Column(
        Text,
        nullable=True,
        comment="Audit message"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Detailed description"
    )
    
    # Data changes
    old_values = Column(
        JSONB,
        nullable=True,
        comment="Previous values (for updates)"
    )
    
    new_values = Column(
        JSONB,
        nullable=True,
        comment="New values (for updates)"
    )
    
    # Request/response data
    request_data = Column(
        JSONB,
        nullable=True,
        comment="Request data"
    )
    
    response_data = Column(
        JSONB,
        nullable=True,
        comment="Response data"
    )
    
    # Error information
    error_code = Column(
        String(50),
        nullable=True,
        comment="Error code"
    )
    
    error_message = Column(
        Text,
        nullable=True,
        comment="Error message"
    )
    
    stack_trace = Column(
        Text,
        nullable=True,
        comment="Error stack trace"
    )
    
    # Performance metrics
    duration_ms = Column(
        Integer,
        nullable=True,
        comment="Operation duration in milliseconds"
    )
    
    # Additional metadata
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional audit metadata"
    )
    
    tags = Column(
        String(500),
        nullable=True,
        comment="Comma-separated tags"
    )
    
    # Compliance and retention
    retention_days = Column(
        Integer,
        nullable=True,
        comment="Retention period in days"
    )
    
    is_sensitive = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Contains sensitive data"
    )
    
    compliance_flags = Column(
        JSONB,
        nullable=True,
        comment="Compliance-related flags"
    )
    
    # Relationships
    user = relationship(
        "User",
        back_populates="audit_logs"
    )
    
    application = relationship(
        "Application"
    )
    
    def __repr__(self) -> str:
        return f"<AuditLog(id={self.id}, action={self.action}, user_id={self.user_id})>"
    
    @property
    def is_successful(self) -> bool:
        """Check if operation was successful."""
        return self.status == AuditStatus.SUCCESS
    
    @property
    def is_critical(self) -> bool:
        """Check if audit entry is critical."""
        return self.level == AuditLevel.CRITICAL
    
    @property
    def has_error(self) -> bool:
        """Check if audit entry has error information."""
        return bool(self.error_code or self.error_message)
    
    @property
    def has_data_changes(self) -> bool:
        """Check if audit entry contains data changes."""
        return bool(self.old_values or self.new_values)
    
    def get_changes_summary(self) -> Dict[str, Any]:
        """Get summary of data changes."""
        if not self.has_data_changes:
            return {}
        
        summary = {
            "changed_fields": [],
            "added_fields": [],
            "removed_fields": []
        }
        
        old_vals = self.old_values or {}
        new_vals = self.new_values or {}
        
        # Find changed fields
        for key in set(old_vals.keys()) & set(new_vals.keys()):
            if old_vals[key] != new_vals[key]:
                summary["changed_fields"].append({
                    "field": key,
                    "old_value": old_vals[key],
                    "new_value": new_vals[key]
                })
        
        # Find added fields
        for key in set(new_vals.keys()) - set(old_vals.keys()):
            summary["added_fields"].append({
                "field": key,
                "value": new_vals[key]
            })
        
        # Find removed fields
        for key in set(old_vals.keys()) - set(new_vals.keys()):
            summary["removed_fields"].append({
                "field": key,
                "value": old_vals[key]
            })
        
        return summary
    
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
        """Add tag to audit entry."""
        if self.tags:
            tags = [t.strip() for t in self.tags.split(",") if t.strip()]
            if tag not in tags:
                tags.append(tag)
                self.tags = ",".join(tags)
        else:
            self.tags = tag
    
    def remove_tag(self, tag: str) -> None:
        """Remove tag from audit entry."""
        if self.tags:
            tags = [t.strip() for t in self.tags.split(",") if t.strip() and t != tag]
            self.tags = ",".join(tags) if tags else None
    
    def get_tags(self) -> list[str]:
        """Get list of tags."""
        if self.tags:
            return [t.strip() for t in self.tags.split(",") if t.strip()]
        return []
    
    def set_error(self, error_code: str = None, error_message: str = None, stack_trace: str = None) -> None:
        """Set error information."""
        self.status = AuditStatus.FAILURE
        if error_code:
            self.error_code = error_code
        if error_message:
            self.error_message = error_message
        if stack_trace:
            self.stack_trace = stack_trace
    
    def set_duration(self, start_time: datetime, end_time: datetime = None) -> None:
        """Set operation duration."""
        if end_time is None:
            end_time = datetime.utcnow()
        
        duration = end_time - start_time
        self.duration_ms = int(duration.total_seconds() * 1000)
    
    @classmethod
    def create_audit_entry(
        cls,
        action: str,
        user_id: str = None,
        resource_type: str = None,
        resource_id: str = None,
        message: str = None,
        **kwargs
    ) -> 'AuditLog':
        """Create new audit entry."""
        return cls(
            action=action,
            user_id=user_id,
            resource_type=resource_type,
            resource_id=resource_id,
            message=message,
            **kwargs
        )


class AuditTrail(BaseModel, TimestampMixin):
    """Audit trail model for tracking related audit entries."""
    
    __tablename__ = "audit_trail"
    
    # Trail information
    name = Column(
        String(200),
        nullable=False,
        comment="Trail name"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Trail description"
    )
    
    # Context
    resource_type = Column(
        String(100),
        nullable=True,
        index=True,
        comment="Type of resource being tracked"
    )
    
    resource_id = Column(
        String(255),
        nullable=True,
        index=True,
        comment="ID of resource being tracked"
    )
    
    # Trail properties
    start_time = Column(
        DateTime(timezone=True),
        nullable=False,
        comment="Trail start time"
    )
    
    end_time = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Trail end time"
    )
    
    status = Column(
        String(20),
        default="active",
        nullable=False,
        comment="Trail status"
    )
    
    # Metadata
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Trail metadata"
    )
    
    # Relationships
    entries = relationship(
        "AuditTrailEntry",
        back_populates="trail",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<AuditTrail(id={self.id}, name={self.name}, status={self.status})>"
    
    @property
    def is_active(self) -> bool:
        """Check if trail is active."""
        return self.status == "active"
    
    @property
    def entry_count(self) -> int:
        """Get count of trail entries."""
        return len(self.entries)
    
    def add_entry(self, audit_log_id: str, sequence: int = None) -> 'AuditTrailEntry':
        """Add audit log entry to trail."""
        if sequence is None:
            sequence = len(self.entries) + 1
        
        entry = AuditTrailEntry(
            trail_id=self.id,
            audit_log_id=audit_log_id,
            sequence=sequence
        )
        self.entries.append(entry)
        return entry
    
    def close_trail(self, end_time: datetime = None) -> None:
        """Close the audit trail."""
        self.status = "closed"
        self.end_time = end_time or datetime.utcnow()


class AuditTrailEntry(BaseModel, TimestampMixin):
    """Audit trail entry model for linking audit logs to trails."""
    
    __tablename__ = "audit_trail_entry"
    
    # Foreign keys
    trail_id = Column(
        UUID(as_uuid=True),
        ForeignKey("audit_trail.id"),
        nullable=False,
        comment="Audit trail ID"
    )
    
    audit_log_id = Column(
        UUID(as_uuid=True),
        ForeignKey("audit_log.id"),
        nullable=False,
        comment="Audit log ID"
    )
    
    # Entry properties
    sequence = Column(
        Integer,
        nullable=False,
        comment="Entry sequence in trail"
    )
    
    notes = Column(
        Text,
        nullable=True,
        comment="Additional notes for this entry"
    )
    
    # Relationships
    trail = relationship(
        "AuditTrail",
        back_populates="entries"
    )
    
    audit_log = relationship(
        "AuditLog"
    )
    
    def __repr__(self) -> str:
        return f"<AuditTrailEntry(id={self.id}, trail_id={self.trail_id}, sequence={self.sequence})>"