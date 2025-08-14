"""Database mixins for common functionality."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, String, DateTime, Boolean, Text, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.ext.declarative import declared_attr


class TimestampMixin:
    """Mixin for timestamp fields."""
    
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        comment="Creation timestamp"
    )
    
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="Last update timestamp"
    )


class SoftDeleteMixin:
    """Mixin for soft delete functionality."""
    
    is_deleted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Soft delete flag"
    )
    
    deleted_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Deletion timestamp"
    )
    
    def soft_delete(self) -> None:
        """Mark record as deleted."""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
    
    def restore(self) -> None:
        """Restore soft deleted record."""
        self.is_deleted = False
        self.deleted_at = None
    
    @property
    def is_active(self) -> bool:
        """Check if record is active (not deleted)."""
        return not self.is_deleted


class AuditMixin:
    """Mixin for audit trail functionality."""
    
    created_by = Column(
        PGUUID(as_uuid=True),
        nullable=True,
        comment="User who created the record"
    )
    
    updated_by = Column(
        PGUUID(as_uuid=True),
        nullable=True,
        comment="User who last updated the record"
    )
    
    created_by_name = Column(
        String(100),
        nullable=True,
        comment="Name of user who created the record"
    )
    
    updated_by_name = Column(
        String(100),
        nullable=True,
        comment="Name of user who last updated the record"
    )
    
    def set_created_by(self, user_id: UUID, user_name: str) -> None:
        """Set creation audit information."""
        self.created_by = user_id
        self.created_by_name = user_name
    
    def set_updated_by(self, user_id: UUID, user_name: str) -> None:
        """Set update audit information."""
        self.updated_by = user_id
        self.updated_by_name = user_name


class VersionMixin:
    """Mixin for optimistic locking with version control."""
    
    version = Column(
        String(50),
        default="1.0.0",
        nullable=False,
        comment="Record version for optimistic locking"
    )
    
    def increment_version(self) -> None:
        """Increment version number."""
        if self.version:
            parts = self.version.split(".")
            if len(parts) == 3:
                try:
                    patch = int(parts[2]) + 1
                    self.version = f"{parts[0]}.{parts[1]}.{patch}"
                except ValueError:
                    self.version = "1.0.1"
            else:
                self.version = "1.0.1"
        else:
            self.version = "1.0.0"


class MetadataMixin:
    """Mixin for storing additional metadata."""
    
    metadata = Column(
        Text,
        nullable=True,
        comment="Additional metadata in JSON format"
    )
    
    tags = Column(
        String(500),
        nullable=True,
        comment="Comma-separated tags"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Description or notes"
    )
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the record."""
        if self.tags:
            tags_list = [t.strip() for t in self.tags.split(",")]
            if tag not in tags_list:
                tags_list.append(tag)
                self.tags = ",".join(tags_list)
        else:
            self.tags = tag
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the record."""
        if self.tags:
            tags_list = [t.strip() for t in self.tags.split(",")]
            if tag in tags_list:
                tags_list.remove(tag)
                self.tags = ",".join(tags_list) if tags_list else None
    
    def get_tags(self) -> list[str]:
        """Get list of tags."""
        if self.tags:
            return [t.strip() for t in self.tags.split(",") if t.strip()]
        return []


class StatusMixin:
    """Mixin for status tracking."""
    
    status = Column(
        String(50),
        default="active",
        nullable=False,
        comment="Record status"
    )
    
    status_reason = Column(
        Text,
        nullable=True,
        comment="Reason for current status"
    )
    
    status_changed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="When status was last changed"
    )
    
    status_changed_by = Column(
        PGUUID(as_uuid=True),
        nullable=True,
        comment="User who changed the status"
    )
    
    def change_status(self, new_status: str, reason: Optional[str] = None, 
                     changed_by: Optional[UUID] = None) -> None:
        """Change the status of the record."""
        self.status = new_status
        self.status_reason = reason
        self.status_changed_at = datetime.utcnow()
        self.status_changed_by = changed_by
    
    @property
    def is_active_status(self) -> bool:
        """Check if status is active."""
        return self.status.lower() in ["active", "enabled", "published"]
    
    @property
    def is_inactive_status(self) -> bool:
        """Check if status is inactive."""
        return self.status.lower() in ["inactive", "disabled", "draft", "suspended"]