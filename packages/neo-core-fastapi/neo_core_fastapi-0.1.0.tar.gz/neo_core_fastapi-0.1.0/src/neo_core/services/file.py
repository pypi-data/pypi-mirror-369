"""File management services."""

from typing import List, Optional, Dict, Any, Union, BinaryIO
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import os
import hashlib
import mimetypes
from pathlib import Path

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from pydantic import BaseModel, validator

from .base import BaseService, ServiceException, NotFoundError, ValidationException, DuplicateError
from .crud import FileCRUDService
from ..models.file import File, FileVersion, FileShare, FileAccessLog
from ..models.file import FileStatus, FileType, StorageProvider, AccessLevel
from ..config import CoreSettings


class FileCreateSchema(BaseModel):
    """Schema for creating a file."""
    filename: str
    original_filename: Optional[str] = None
    file_type: Optional[FileType] = None
    mime_type: Optional[str] = None
    file_size: int
    file_hash: Optional[str] = None
    storage_provider: StorageProvider = StorageProvider.LOCAL
    storage_path: str
    storage_url: Optional[str] = None
    owner_id: UUID
    application_id: Optional[UUID] = None
    parent_folder_id: Optional[UUID] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_public: bool = False
    access_level: AccessLevel = AccessLevel.PRIVATE
    
    @validator('filename')
    def validate_filename(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError('Filename cannot be empty')
        return v.strip()
    
    @validator('file_size')
    def validate_file_size(cls, v):
        if v < 0:
            raise ValueError('File size cannot be negative')
        return v


class FileUpdateSchema(BaseModel):
    """Schema for updating a file."""
    filename: Optional[str] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = None
    access_level: Optional[AccessLevel] = None
    parent_folder_id: Optional[UUID] = None


class FileVersionCreateSchema(BaseModel):
    """Schema for creating a file version."""
    file_id: UUID
    version_number: str
    file_size: int
    file_hash: str
    storage_path: str
    storage_url: Optional[str] = None
    change_description: Optional[str] = None
    uploaded_by: UUID


class FileShareCreateSchema(BaseModel):
    """Schema for creating a file share."""
    file_id: UUID
    shared_with_user_id: Optional[UUID] = None
    shared_with_role_id: Optional[UUID] = None
    shared_with_group_id: Optional[UUID] = None
    access_level: AccessLevel = AccessLevel.READ
    expires_at: Optional[datetime] = None
    share_token: Optional[str] = None
    password: Optional[str] = None
    max_downloads: Optional[int] = None
    allow_upload: bool = False
    message: Optional[str] = None


class FileShareUpdateSchema(BaseModel):
    """Schema for updating a file share."""
    access_level: Optional[AccessLevel] = None
    expires_at: Optional[datetime] = None
    password: Optional[str] = None
    max_downloads: Optional[int] = None
    allow_upload: Optional[bool] = None
    message: Optional[str] = None
    is_active: Optional[bool] = None


class FileService(BaseService):
    """Service for file management."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        self.file_crud = FileCRUDService(settings)
        self.max_file_size = 100 * 1024 * 1024  # 100MB default
        self.allowed_extensions = None  # None means all extensions allowed
        self.storage_base_path = "uploads"
    
    def create_file(self, file_data: FileCreateSchema) -> File:
        """Create a new file record."""
        try:
            # Validate input
            file_data = self.validate_input(file_data, FileCreateSchema)
            
            # Validate file size
            if file_data.file_size > self.max_file_size:
                raise ValidationException(f"File size exceeds maximum allowed size of {self.max_file_size} bytes")
            
            # Validate file extension if restrictions exist
            if self.allowed_extensions:
                file_ext = Path(file_data.filename).suffix.lower()
                if file_ext not in self.allowed_extensions:
                    raise ValidationException(f"File extension {file_ext} is not allowed")
            
            # Auto-detect file type and mime type if not provided
            if not file_data.file_type:
                file_data.file_type = self._detect_file_type(file_data.filename)
            
            if not file_data.mime_type:
                file_data.mime_type = self._detect_mime_type(file_data.filename)
            
            # Set original filename if not provided
            if not file_data.original_filename:
                file_data.original_filename = file_data.filename
            
            # Create file data
            create_data = {
                "id": uuid4(),
                "filename": file_data.filename,
                "original_filename": file_data.original_filename,
                "file_type": file_data.file_type,
                "mime_type": file_data.mime_type,
                "file_size": file_data.file_size,
                "file_hash": file_data.file_hash,
                "storage_provider": file_data.storage_provider,
                "storage_path": file_data.storage_path,
                "storage_url": file_data.storage_url,
                "status": FileStatus.ACTIVE,
                "owner_id": file_data.owner_id,
                "application_id": file_data.application_id,
                "parent_folder_id": file_data.parent_folder_id,
                "description": file_data.description,
                "tags": file_data.tags or [],
                "metadata": file_data.metadata or {},
                "is_public": file_data.is_public,
                "access_level": file_data.access_level,
                "version": "1.0",
                "download_count": 0,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create file
            file = self.file_crud.create(create_data)
            
            # Create initial version
            self._create_initial_version(file)
            
            # Log file creation
            self._log_file_access(
                file.id,
                file_data.owner_id,
                "create",
                "File created"
            )
            
            self.log_operation("create_file", {
                "file_id": file.id,
                "filename": file.filename,
                "file_size": file.file_size,
                "owner_id": file.owner_id
            })
            
            return file
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create file")
    
    def get_file(self, file_id: UUID) -> Optional[File]:
        """Get a file by ID."""
        return self.file_crud.get(file_id)
    
    def get_file_by_path(self, storage_path: str) -> Optional[File]:
        """Get a file by storage path."""
        try:
            return (
                self.db.query(File)
                .filter(File.storage_path == storage_path)
                .first()
            )
        except Exception as e:
            self.handle_db_error(e, "get file by path")
    
    def update_file(self, file_id: UUID, file_data: FileUpdateSchema) -> File:
        """Update a file."""
        try:
            # Validate input
            file_data = self.validate_input(file_data, FileUpdateSchema)
            
            # Get existing file
            file = self.file_crud.get(file_id)
            if not file:
                raise NotFoundError("File", file_id)
            
            # Update file data
            update_data = file_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            # Update file
            updated_file = self.file_crud.update(file_id, update_data)
            
            self.log_operation("update_file", {
                "file_id": file_id,
                "updated_fields": list(update_data.keys())
            })
            
            return updated_file
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "update file")
    
    def delete_file(self, file_id: UUID, user_id: UUID, permanent: bool = False) -> bool:
        """Delete a file (soft delete by default)."""
        try:
            file = self.file_crud.get(file_id)
            if not file:
                raise NotFoundError("File", file_id)
            
            # Check permissions
            if not self._check_file_permission(file, user_id, "delete"):
                raise ValidationException("Insufficient permissions to delete file")
            
            if permanent:
                # Permanent deletion
                success = self.file_crud.delete(file_id)
                
                # TODO: Delete physical file from storage
                # self._delete_physical_file(file.storage_path)
                
                action = "permanent_delete"
            else:
                # Soft deletion
                self.file_crud.update(file_id, {
                    "status": FileStatus.DELETED,
                    "deleted_at": datetime.utcnow(),
                    "deleted_by": user_id,
                    "updated_at": datetime.utcnow()
                })
                success = True
                action = "soft_delete"
            
            if success:
                # Log file deletion
                self._log_file_access(
                    file_id,
                    user_id,
                    action,
                    f"File {action.replace('_', ' ')}"
                )
                
                self.log_operation("delete_file", {
                    "file_id": file_id,
                    "permanent": permanent,
                    "user_id": user_id
                })
            
            return success
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "delete file")
    
    def restore_file(self, file_id: UUID, user_id: UUID) -> File:
        """Restore a soft-deleted file."""
        try:
            file = self.file_crud.get(file_id)
            if not file:
                raise NotFoundError("File", file_id)
            
            if file.status != FileStatus.DELETED:
                raise ValidationException("File is not deleted")
            
            # Check permissions
            if not self._check_file_permission(file, user_id, "restore"):
                raise ValidationException("Insufficient permissions to restore file")
            
            # Restore file
            updated_file = self.file_crud.update(file_id, {
                "status": FileStatus.ACTIVE,
                "deleted_at": None,
                "deleted_by": None,
                "updated_at": datetime.utcnow()
            })
            
            # Log file restoration
            self._log_file_access(
                file_id,
                user_id,
                "restore",
                "File restored"
            )
            
            return updated_file
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "restore file")
    
    def list_files(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        order_by: str = "created_at",
        order_desc: bool = True
    ) -> List[File]:
        """List files with filtering and pagination."""
        return self.file_crud.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=order_by,
            order_desc=order_desc
        )
    
    def get_user_files(
        self,
        user_id: UUID,
        include_shared: bool = True,
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        """Get files owned by or shared with a user."""
        try:
            query = self.db.query(File).filter(
                File.status == FileStatus.ACTIVE
            )
            
            if include_shared:
                # Include files owned by user or shared with user
                shared_file_ids = (
                    self.db.query(FileShare.file_id)
                    .filter(
                        FileShare.shared_with_user_id == user_id,
                        FileShare.is_active == True,
                        or_(
                            FileShare.expires_at.is_(None),
                            FileShare.expires_at > datetime.utcnow()
                        )
                    )
                    .subquery()
                )
                
                query = query.filter(
                    or_(
                        File.owner_id == user_id,
                        File.id.in_(shared_file_ids)
                    )
                )
            else:
                # Only files owned by user
                query = query.filter(File.owner_id == user_id)
            
            return (
                query.order_by(File.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            self.handle_db_error(e, "get user files")
    
    def search_files(
        self,
        query: str,
        user_id: Optional[UUID] = None,
        file_types: Optional[List[FileType]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[File]:
        """Search files by filename, description, or tags."""
        try:
            db_query = self.db.query(File).filter(
                File.status == FileStatus.ACTIVE
            )
            
            # Text search
            search_filter = or_(
                File.filename.ilike(f"%{query}%"),
                File.original_filename.ilike(f"%{query}%"),
                File.description.ilike(f"%{query}%")
            )
            
            # Tag search (assuming tags are stored as JSON array)
            # This would need to be adapted based on your database
            # search_filter = or_(search_filter, File.tags.contains([query]))
            
            db_query = db_query.filter(search_filter)
            
            # Filter by user access
            if user_id:
                # Include files owned by user or shared with user or public files
                shared_file_ids = (
                    self.db.query(FileShare.file_id)
                    .filter(
                        FileShare.shared_with_user_id == user_id,
                        FileShare.is_active == True,
                        or_(
                            FileShare.expires_at.is_(None),
                            FileShare.expires_at > datetime.utcnow()
                        )
                    )
                    .subquery()
                )
                
                db_query = db_query.filter(
                    or_(
                        File.owner_id == user_id,
                        File.id.in_(shared_file_ids),
                        File.is_public == True
                    )
                )
            else:
                # Only public files for anonymous users
                db_query = db_query.filter(File.is_public == True)
            
            # Filter by file types
            if file_types:
                db_query = db_query.filter(File.file_type.in_(file_types))
            
            return (
                db_query.order_by(File.updated_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            self.handle_db_error(e, "search files")
    
    def create_file_version(self, version_data: FileVersionCreateSchema) -> FileVersion:
        """Create a new version of a file."""
        try:
            # Validate input
            version_data = self.validate_input(version_data, FileVersionCreateSchema)
            
            # Check if file exists
            file = self.file_crud.get(version_data.file_id)
            if not file:
                raise NotFoundError("File", version_data.file_id)
            
            # Create version data
            create_data = {
                "id": uuid4(),
                "file_id": version_data.file_id,
                "version_number": version_data.version_number,
                "file_size": version_data.file_size,
                "file_hash": version_data.file_hash,
                "storage_path": version_data.storage_path,
                "storage_url": version_data.storage_url,
                "change_description": version_data.change_description,
                "uploaded_by": version_data.uploaded_by,
                "created_at": datetime.utcnow()
            }
            
            # Create version
            version = FileVersion(**create_data)
            self.db.add(version)
            
            # Update file with new version info
            self.file_crud.update(version_data.file_id, {
                "version": version_data.version_number,
                "file_size": version_data.file_size,
                "file_hash": version_data.file_hash,
                "storage_path": version_data.storage_path,
                "storage_url": version_data.storage_url,
                "updated_at": datetime.utcnow()
            })
            
            self.db.commit()
            self.db.refresh(version)
            
            # Log version creation
            self._log_file_access(
                version_data.file_id,
                version_data.uploaded_by,
                "version_create",
                f"New version {version_data.version_number} created"
            )
            
            return version
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create file version")
    
    def get_file_versions(self, file_id: UUID) -> List[FileVersion]:
        """Get all versions of a file."""
        try:
            return (
                self.db.query(FileVersion)
                .filter(FileVersion.file_id == file_id)
                .order_by(FileVersion.created_at.desc())
                .all()
            )
        except Exception as e:
            self.handle_db_error(e, "get file versions")
    
    def create_file_share(self, share_data: FileShareCreateSchema) -> FileShare:
        """Create a file share."""
        try:
            # Validate input
            share_data = self.validate_input(share_data, FileShareCreateSchema)
            
            # Check if file exists
            file = self.file_crud.get(share_data.file_id)
            if not file:
                raise NotFoundError("File", share_data.file_id)
            
            # Generate share token if not provided
            if not share_data.share_token:
                share_data.share_token = self._generate_share_token()
            
            # Create share data
            create_data = {
                "id": uuid4(),
                "file_id": share_data.file_id,
                "shared_with_user_id": share_data.shared_with_user_id,
                "shared_with_role_id": share_data.shared_with_role_id,
                "shared_with_group_id": share_data.shared_with_group_id,
                "access_level": share_data.access_level,
                "expires_at": share_data.expires_at,
                "share_token": share_data.share_token,
                "password": share_data.password,
                "max_downloads": share_data.max_downloads,
                "allow_upload": share_data.allow_upload,
                "message": share_data.message,
                "download_count": 0,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create share
            share = FileShare(**create_data)
            self.db.add(share)
            self.db.commit()
            self.db.refresh(share)
            
            self.log_operation("create_file_share", {
                "share_id": share.id,
                "file_id": share.file_id,
                "access_level": share.access_level
            })
            
            return share
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create file share")
    
    def get_file_share(self, share_id: UUID) -> Optional[FileShare]:
        """Get a file share by ID."""
        try:
            return self.db.query(FileShare).filter(
                FileShare.id == share_id
            ).first()
        except Exception as e:
            self.handle_db_error(e, "get file share")
    
    def get_file_share_by_token(self, share_token: str) -> Optional[FileShare]:
        """Get a file share by token."""
        try:
            return (
                self.db.query(FileShare)
                .filter(
                    FileShare.share_token == share_token,
                    FileShare.is_active == True,
                    or_(
                        FileShare.expires_at.is_(None),
                        FileShare.expires_at > datetime.utcnow()
                    )
                )
                .first()
            )
        except Exception as e:
            self.handle_db_error(e, "get file share by token")
    
    def update_file_share(self, share_id: UUID, share_data: FileShareUpdateSchema) -> FileShare:
        """Update a file share."""
        try:
            # Validate input
            share_data = self.validate_input(share_data, FileShareUpdateSchema)
            
            # Get existing share
            share = self.get_file_share(share_id)
            if not share:
                raise NotFoundError("FileShare", share_id)
            
            # Update share data
            update_data = share_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            # Update share
            for key, value in update_data.items():
                setattr(share, key, value)
            
            self.db.commit()
            self.db.refresh(share)
            
            return share
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "update file share")
    
    def revoke_file_share(self, share_id: UUID) -> bool:
        """Revoke a file share."""
        try:
            share = self.get_file_share(share_id)
            if not share:
                raise NotFoundError("FileShare", share_id)
            
            # Deactivate share
            share.is_active = False
            share.updated_at = datetime.utcnow()
            self.db.commit()
            
            self.log_operation("revoke_file_share", {
                "share_id": share_id,
                "file_id": share.file_id
            })
            
            return True
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "revoke file share")
    
    def get_file_shares(self, file_id: UUID) -> List[FileShare]:
        """Get all shares for a file."""
        try:
            return (
                self.db.query(FileShare)
                .filter(FileShare.file_id == file_id)
                .order_by(FileShare.created_at.desc())
                .all()
            )
        except Exception as e:
            self.handle_db_error(e, "get file shares")
    
    def record_file_access(
        self,
        file_id: UUID,
        user_id: Optional[UUID],
        action: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> FileAccessLog:
        """Record file access."""
        return self._log_file_access(
            file_id,
            user_id,
            action,
            f"File {action}",
            client_ip,
            user_agent,
            additional_info
        )
    
    def get_file_access_logs(
        self,
        file_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[FileAccessLog]:
        """Get access logs for a file."""
        try:
            return (
                self.db.query(FileAccessLog)
                .filter(FileAccessLog.file_id == file_id)
                .order_by(FileAccessLog.accessed_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            self.handle_db_error(e, "get file access logs")
    
    def increment_download_count(self, file_id: UUID) -> bool:
        """Increment file download count."""
        try:
            file = self.file_crud.get(file_id)
            if not file:
                return False
            
            self.file_crud.update(file_id, {
                "download_count": file.download_count + 1,
                "last_accessed_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            return True
        except Exception as e:
            self.handle_db_error(e, "increment download count")
    
    def cleanup_expired_shares(self) -> int:
        """Clean up expired file shares."""
        try:
            current_time = datetime.utcnow()
            
            # Deactivate expired shares
            updated_count = (
                self.db.query(FileShare)
                .filter(
                    FileShare.expires_at < current_time,
                    FileShare.is_active == True
                )
                .update({
                    "is_active": False,
                    "updated_at": current_time
                })
            )
            
            self.db.commit()
            
            self.log_operation("cleanup_expired_shares", {
                "deactivated_count": updated_count
            })
            
            return updated_count
        except Exception as e:
            self.db.rollback()
            self.handle_db_error(e, "cleanup expired shares")
    
    def _create_initial_version(self, file: File) -> FileVersion:
        """Create initial version for a file."""
        version_data = {
            "id": uuid4(),
            "file_id": file.id,
            "version_number": "1.0",
            "file_size": file.file_size,
            "file_hash": file.file_hash,
            "storage_path": file.storage_path,
            "storage_url": file.storage_url,
            "change_description": "Initial version",
            "uploaded_by": file.owner_id,
            "created_at": datetime.utcnow()
        }
        
        version = FileVersion(**version_data)
        self.db.add(version)
        self.db.commit()
        self.db.refresh(version)
        
        return version
    
    def _detect_file_type(self, filename: str) -> FileType:
        """Detect file type from filename."""
        ext = Path(filename).suffix.lower()
        
        # Image files
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp']:
            return FileType.IMAGE
        
        # Video files
        elif ext in ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv']:
            return FileType.VIDEO
        
        # Audio files
        elif ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.wma']:
            return FileType.AUDIO
        
        # Document files
        elif ext in ['.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt']:
            return FileType.DOCUMENT
        
        # Spreadsheet files
        elif ext in ['.xls', '.xlsx', '.csv', '.ods']:
            return FileType.SPREADSHEET
        
        # Presentation files
        elif ext in ['.ppt', '.pptx', '.odp']:
            return FileType.PRESENTATION
        
        # Archive files
        elif ext in ['.zip', '.rar', '.7z', '.tar', '.gz', '.bz2']:
            return FileType.ARCHIVE
        
        # Code files
        elif ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.php', '.rb', '.go']:
            return FileType.CODE
        
        else:
            return FileType.OTHER
    
    def _detect_mime_type(self, filename: str) -> str:
        """Detect MIME type from filename."""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or 'application/octet-stream'
    
    def _check_file_permission(self, file: File, user_id: UUID, action: str) -> bool:
        """Check if user has permission to perform action on file."""
        # Owner has all permissions
        if file.owner_id == user_id:
            return True
        
        # Public files allow read access
        if file.is_public and action in ['read', 'download']:
            return True
        
        # Check shared permissions
        share = (
            self.db.query(FileShare)
            .filter(
                FileShare.file_id == file.id,
                FileShare.shared_with_user_id == user_id,
                FileShare.is_active == True,
                or_(
                    FileShare.expires_at.is_(None),
                    FileShare.expires_at > datetime.utcnow()
                )
            )
            .first()
        )
        
        if share:
            if action in ['read', 'download']:
                return True
            elif action == 'write' and share.access_level in [AccessLevel.WRITE, AccessLevel.ADMIN]:
                return True
            elif action == 'delete' and share.access_level == AccessLevel.ADMIN:
                return True
        
        return False
    
    def _generate_share_token(self) -> str:
        """Generate a secure share token."""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _log_file_access(
        self,
        file_id: UUID,
        user_id: Optional[UUID],
        action: str,
        description: str,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> FileAccessLog:
        """Log file access."""
        try:
            log_data = {
                "id": uuid4(),
                "file_id": file_id,
                "user_id": user_id,
                "action": action,
                "description": description,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "additional_info": additional_info or {},
                "accessed_at": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            
            log = FileAccessLog(**log_data)
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)
            
            return log
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to log file access: {str(e)}")
            # Don't raise exception for logging failures
            return None
    
    def get_file_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get file statistics."""
        try:
            # Default to last 30 days if no time range specified
            if not start_time:
                start_time = datetime.utcnow() - timedelta(days=30)
            if not end_time:
                end_time = datetime.utcnow()
            
            # Base query
            query = self.db.query(File).filter(
                File.created_at >= start_time,
                File.created_at <= end_time
            )
            
            # Total files
            total_files = query.count()
            
            # Active files
            active_files = query.filter(File.status == FileStatus.ACTIVE).count()
            
            # Files by type
            type_counts = {}
            for file_type in FileType:
                count = query.filter(File.file_type == file_type).count()
                type_counts[file_type.value] = count
            
            # Total storage used
            total_size = query.with_entities(func.sum(File.file_size)).scalar() or 0
            
            # Most downloaded files
            top_files = (
                query.filter(File.status == FileStatus.ACTIVE)
                .order_by(File.download_count.desc())
                .limit(10)
                .all()
            )
            
            return {
                "period": {
                    "start_time": start_time,
                    "end_time": end_time
                },
                "total_files": total_files,
                "active_files": active_files,
                "type_counts": type_counts,
                "total_storage_bytes": total_size,
                "top_downloaded_files": [
                    {
                        "id": f.id,
                        "filename": f.filename,
                        "download_count": f.download_count
                    }
                    for f in top_files
                ]
            }
        except Exception as e:
            self.handle_db_error(e, "get file statistics")