"""File models for managing file uploads, storage, and metadata."""

from datetime import datetime
from typing import Optional, Dict, Any, List
from enum import Enum

from sqlalchemy import Column, String, DateTime, Boolean, Text, ForeignKey, Integer, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ..database.base import BaseModel
from ..database.mixins import TimestampMixin, SoftDeleteMixin, AuditMixin


class FileStatus(str, Enum):
    """File status enumeration."""
    UPLOADING = "uploading"
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    PROCESSED = "processed"
    AVAILABLE = "available"
    ARCHIVED = "archived"
    DELETED = "deleted"
    ERROR = "error"
    QUARANTINED = "quarantined"


class FileType(str, Enum):
    """File type enumeration."""
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"
    SPREADSHEET = "spreadsheet"
    PRESENTATION = "presentation"
    ARCHIVE = "archive"
    CODE = "code"
    DATA = "data"
    OTHER = "other"


class StorageProvider(str, Enum):
    """Storage provider enumeration."""
    LOCAL = "local"
    AWS_S3 = "aws_s3"
    AZURE_BLOB = "azure_blob"
    GOOGLE_CLOUD = "google_cloud"
    MINIO = "minio"
    FTP = "ftp"
    SFTP = "sftp"


class AccessLevel(str, Enum):
    """File access level enumeration."""
    PUBLIC = "public"
    PRIVATE = "private"
    RESTRICTED = "restricted"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"


class File(BaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """File model for managing uploaded files and their metadata."""
    
    __tablename__ = "file"
    
    # Basic file information
    filename = Column(
        String(255),
        nullable=False,
        comment="Original filename"
    )
    
    display_name = Column(
        String(255),
        nullable=True,
        comment="Display name for the file"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="File description"
    )
    
    # File properties
    file_type = Column(
        String(20),
        nullable=False,
        index=True,
        comment="File type category"
    )
    
    mime_type = Column(
        String(100),
        nullable=True,
        comment="MIME type"
    )
    
    file_extension = Column(
        String(10),
        nullable=True,
        comment="File extension"
    )
    
    file_size = Column(
        BigInteger,
        nullable=False,
        comment="File size in bytes"
    )
    
    # Storage information
    storage_provider = Column(
        String(20),
        default=StorageProvider.LOCAL,
        nullable=False,
        comment="Storage provider"
    )
    
    storage_path = Column(
        String(500),
        nullable=False,
        comment="Storage path or key"
    )
    
    storage_bucket = Column(
        String(100),
        nullable=True,
        comment="Storage bucket or container"
    )
    
    storage_region = Column(
        String(50),
        nullable=True,
        comment="Storage region"
    )
    
    # File status and processing
    status = Column(
        String(20),
        default=FileStatus.UPLOADING,
        nullable=False,
        index=True,
        comment="File status"
    )
    
    processing_status = Column(
        String(100),
        nullable=True,
        comment="Processing status details"
    )
    
    # Security and access
    access_level = Column(
        String(20),
        default=AccessLevel.PRIVATE,
        nullable=False,
        comment="File access level"
    )
    
    is_public = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="File is publicly accessible"
    )
    
    is_encrypted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="File is encrypted"
    )
    
    encryption_key_id = Column(
        String(255),
        nullable=True,
        comment="Encryption key identifier"
    )
    
    # File hashes and checksums
    md5_hash = Column(
        String(32),
        nullable=True,
        index=True,
        comment="MD5 hash of file content"
    )
    
    sha256_hash = Column(
        String(64),
        nullable=True,
        index=True,
        comment="SHA256 hash of file content"
    )
    
    # Owner and application context
    owner_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=True,
        index=True,
        comment="File owner user ID"
    )
    
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("application.id"),
        nullable=True,
        comment="Application ID"
    )
    
    # URLs and access
    public_url = Column(
        String(500),
        nullable=True,
        comment="Public access URL"
    )
    
    download_url = Column(
        String(500),
        nullable=True,
        comment="Download URL"
    )
    
    thumbnail_url = Column(
        String(500),
        nullable=True,
        comment="Thumbnail URL"
    )
    
    # Usage tracking
    download_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of downloads"
    )
    
    view_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of views"
    )
    
    last_accessed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last access timestamp"
    )
    
    # Expiration and retention
    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="File expiration time"
    )
    
    retention_days = Column(
        Integer,
        nullable=True,
        comment="Retention period in days"
    )
    
    # File metadata
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional file metadata"
    )
    
    exif_data = Column(
        JSONB,
        nullable=True,
        comment="EXIF data for images"
    )
    
    # Categorization
    category = Column(
        String(100),
        nullable=True,
        index=True,
        comment="File category"
    )
    
    tags = Column(
        String(500),
        nullable=True,
        comment="Comma-separated tags"
    )
    
    # Virus scanning
    virus_scan_status = Column(
        String(20),
        nullable=True,
        comment="Virus scan status"
    )
    
    virus_scan_result = Column(
        Text,
        nullable=True,
        comment="Virus scan result details"
    )
    
    virus_scanned_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Virus scan timestamp"
    )
    
    # Relationships
    owner = relationship(
        "User",
        back_populates="files"
    )
    
    application = relationship(
        "Application"
    )
    
    versions = relationship(
        "FileVersion",
        back_populates="file",
        cascade="all, delete-orphan"
    )
    
    shares = relationship(
        "FileShare",
        back_populates="file",
        cascade="all, delete-orphan"
    )
    
    access_logs = relationship(
        "FileAccessLog",
        back_populates="file",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<File(id={self.id}, filename={self.filename}, status={self.status})>"
    
    @property
    def is_available(self) -> bool:
        """Check if file is available for access."""
        return self.status == FileStatus.AVAILABLE and not self.is_deleted
    
    @property
    def is_expired(self) -> bool:
        """Check if file is expired."""
        return self.expires_at and self.expires_at <= datetime.utcnow()
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in MB."""
        return self.file_size / (1024 * 1024) if self.file_size else 0
    
    @property
    def is_image(self) -> bool:
        """Check if file is an image."""
        return self.file_type == FileType.IMAGE
    
    @property
    def is_video(self) -> bool:
        """Check if file is a video."""
        return self.file_type == FileType.VIDEO
    
    @property
    def is_document(self) -> bool:
        """Check if file is a document."""
        return self.file_type == FileType.DOCUMENT
    
    def mark_as_uploaded(self) -> None:
        """Mark file as successfully uploaded."""
        self.status = FileStatus.UPLOADED
    
    def mark_as_available(self) -> None:
        """Mark file as available for access."""
        self.status = FileStatus.AVAILABLE
    
    def mark_as_error(self, error_message: str = None) -> None:
        """Mark file as having an error."""
        self.status = FileStatus.ERROR
        if error_message:
            self.add_metadata("error_message", error_message)
    
    def increment_download_count(self) -> None:
        """Increment download counter."""
        self.download_count += 1
        self.last_accessed_at = datetime.utcnow()
    
    def increment_view_count(self) -> None:
        """Increment view counter."""
        self.view_count += 1
        self.last_accessed_at = datetime.utcnow()
    
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
        """Add tag to file."""
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
    
    def create_version(self, version_number: str = None, **kwargs) -> 'FileVersion':
        """Create new file version."""
        if version_number is None:
            version_count = len(self.versions)
            version_number = f"v{version_count + 1}"
        
        version = FileVersion(
            file_id=self.id,
            version_number=version_number,
            **kwargs
        )
        self.versions.append(version)
        return version
    
    def share_with_user(self, user_id: str, permission: str = "read", expires_at: datetime = None) -> 'FileShare':
        """Share file with user."""
        share = FileShare(
            file_id=self.id,
            shared_with_user_id=user_id,
            permission=permission,
            expires_at=expires_at
        )
        self.shares.append(share)
        return share
    
    def log_access(self, user_id: str = None, action: str = "view", ip_address: str = None) -> 'FileAccessLog':
        """Log file access."""
        log = FileAccessLog(
            file_id=self.id,
            user_id=user_id,
            action=action,
            ip_address=ip_address
        )
        self.access_logs.append(log)
        return log


class FileVersion(BaseModel, TimestampMixin, AuditMixin):
    """File version model for managing file versions."""
    
    __tablename__ = "file_version"
    
    # Foreign key
    file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("file.id"),
        nullable=False,
        index=True,
        comment="File ID"
    )
    
    # Version information
    version_number = Column(
        String(50),
        nullable=False,
        comment="Version number or identifier"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Version description or changelog"
    )
    
    # File properties for this version
    filename = Column(
        String(255),
        nullable=False,
        comment="Filename for this version"
    )
    
    file_size = Column(
        BigInteger,
        nullable=False,
        comment="File size in bytes for this version"
    )
    
    storage_path = Column(
        String(500),
        nullable=False,
        comment="Storage path for this version"
    )
    
    # File hashes
    md5_hash = Column(
        String(32),
        nullable=True,
        comment="MD5 hash for this version"
    )
    
    sha256_hash = Column(
        String(64),
        nullable=True,
        comment="SHA256 hash for this version"
    )
    
    # Version status
    is_current = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="This is the current version"
    )
    
    # Additional metadata
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Version-specific metadata"
    )
    
    # Relationships
    file = relationship(
        "File",
        back_populates="versions"
    )
    
    def __repr__(self) -> str:
        return f"<FileVersion(id={self.id}, file_id={self.file_id}, version={self.version_number})>"
    
    def make_current(self) -> None:
        """Make this version the current one."""
        # Set all other versions as not current
        for version in self.file.versions:
            version.is_current = False
        
        # Set this version as current
        self.is_current = True


class FileShare(BaseModel, TimestampMixin, AuditMixin):
    """File share model for managing file sharing permissions."""
    
    __tablename__ = "file_share"
    
    # Foreign keys
    file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("file.id"),
        nullable=False,
        index=True,
        comment="File ID"
    )
    
    shared_with_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=False,
        index=True,
        comment="User ID file is shared with"
    )
    
    shared_by_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=True,
        comment="User ID who shared the file"
    )
    
    # Share properties
    permission = Column(
        String(20),
        default="read",
        nullable=False,
        comment="Permission level (read, write, admin)"
    )
    
    # Share expiration
    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
        comment="Share expiration time"
    )
    
    # Share status
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Share is active"
    )
    
    # Access tracking
    access_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Number of times accessed"
    )
    
    last_accessed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last access timestamp"
    )
    
    # Additional metadata
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Share metadata"
    )
    
    # Relationships
    file = relationship(
        "File",
        back_populates="shares"
    )
    
    shared_with_user = relationship(
        "User",
        foreign_keys=[shared_with_user_id]
    )
    
    shared_by_user = relationship(
        "User",
        foreign_keys=[shared_by_user_id]
    )
    
    def __repr__(self) -> str:
        return f"<FileShare(id={self.id}, file_id={self.file_id}, permission={self.permission})>"
    
    @property
    def is_expired(self) -> bool:
        """Check if share is expired."""
        return self.expires_at and self.expires_at <= datetime.utcnow()
    
    @property
    def is_valid(self) -> bool:
        """Check if share is valid and active."""
        return self.is_active and not self.is_expired
    
    def revoke(self) -> None:
        """Revoke the file share."""
        self.is_active = False
    
    def access(self) -> None:
        """Record file share access."""
        self.access_count += 1
        self.last_accessed_at = datetime.utcnow()


class FileAccessLog(BaseModel, TimestampMixin):
    """File access log model for tracking file access."""
    
    __tablename__ = "file_access_log"
    
    # Foreign keys
    file_id = Column(
        UUID(as_uuid=True),
        ForeignKey("file.id"),
        nullable=False,
        index=True,
        comment="File ID"
    )
    
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=True,
        index=True,
        comment="User ID (null for anonymous access)"
    )
    
    # Access information
    action = Column(
        String(50),
        nullable=False,
        index=True,
        comment="Action performed (view, download, edit, etc.)"
    )
    
    # Client information
    ip_address = Column(
        String(45),
        nullable=True,
        comment="Client IP address"
    )
    
    user_agent = Column(
        Text,
        nullable=True,
        comment="Client user agent"
    )
    
    # Additional context
    referrer = Column(
        String(500),
        nullable=True,
        comment="HTTP referrer"
    )
    
    # Additional metadata
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional access metadata"
    )
    
    # Relationships
    file = relationship(
        "File",
        back_populates="access_logs"
    )
    
    user = relationship(
        "User"
    )
    
    def __repr__(self) -> str:
        return f"<FileAccessLog(id={self.id}, file_id={self.file_id}, action={self.action})>"