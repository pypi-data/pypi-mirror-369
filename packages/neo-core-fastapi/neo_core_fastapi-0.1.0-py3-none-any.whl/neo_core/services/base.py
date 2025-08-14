"""Base service classes providing common functionality for all services."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, TypeVar, Generic, Union
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func, and_, or_
from sqlalchemy.exc import IntegrityError, NoResultFound
from pydantic import BaseModel

from ..database.base import BaseModel as DBBaseModel
from ..database.session import get_db_session, get_async_db_session
from ..config import CoreSettings

# Type variables for generic typing
ModelType = TypeVar("ModelType", bound=DBBaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class ServiceException(Exception):
    """Base exception for service layer errors."""
    
    def __init__(self, message: str, code: str = None, details: Dict[str, Any] = None):
        self.message = message
        self.code = code or "SERVICE_ERROR"
        self.details = details or {}
        super().__init__(self.message)


class ValidationException(ServiceException):
    """Exception for validation errors."""
    
    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        super().__init__(message, "VALIDATION_ERROR", details)
        self.field = field


class NotFoundError(ServiceException):
    """Exception for resource not found errors."""
    
    def __init__(self, resource: str, identifier: Any = None):
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        super().__init__(message, "NOT_FOUND")
        self.resource = resource
        self.identifier = identifier


class DuplicateError(ServiceException):
    """Exception for duplicate resource errors."""
    
    def __init__(self, resource: str, field: str = None, value: Any = None):
        message = f"Duplicate {resource}"
        if field and value:
            message += f" with {field}: {value}"
        super().__init__(message, "DUPLICATE_ERROR")
        self.resource = resource
        self.field = field
        self.value = value


class PermissionError(ServiceException):
    """Exception for permission/authorization errors."""
    
    def __init__(self, action: str, resource: str = None):
        message = f"Permission denied for action: {action}"
        if resource:
            message += f" on resource: {resource}"
        super().__init__(message, "PERMISSION_DENIED")
        self.action = action
        self.resource = resource


class BaseService(ABC):
    """Abstract base service class providing common functionality."""
    
    def __init__(self, settings: CoreSettings = None):
        self.settings = settings or CoreSettings()
        self._db_session: Optional[Session] = None
        self._async_db_session: Optional[AsyncSession] = None
    
    @property
    def db(self) -> Session:
        """Get database session."""
        if self._db_session is None:
            self._db_session = next(get_db_session())
        return self._db_session
    
    @property
    def async_db(self) -> AsyncSession:
        """Get async database session."""
        if self._async_db_session is None:
            self._async_db_session = next(get_async_db_session())
        return self._async_db_session
    
    def set_db_session(self, session: Session) -> None:
        """Set database session."""
        self._db_session = session
    
    def set_async_db_session(self, session: AsyncSession) -> None:
        """Set async database session."""
        self._async_db_session = session
    
    def close_sessions(self) -> None:
        """Close database sessions."""
        if self._db_session:
            self._db_session.close()
            self._db_session = None
        if self._async_db_session:
            # Note: AsyncSession should be closed with await
            self._async_db_session = None
    
    def validate_input(self, data: Any, schema: Type[BaseModel]) -> BaseModel:
        """Validate input data against schema."""
        try:
            return schema(**data) if isinstance(data, dict) else schema.parse_obj(data)
        except Exception as e:
            raise ValidationException(f"Invalid input data: {str(e)}")
    
    def handle_db_error(self, error: Exception, operation: str = "database operation") -> None:
        """Handle database errors and convert to service exceptions."""
        if isinstance(error, IntegrityError):
            if "unique" in str(error).lower():
                raise DuplicateError("Resource", details={"original_error": str(error)})
            else:
                raise ServiceException(f"Database integrity error during {operation}", "INTEGRITY_ERROR")
        elif isinstance(error, NoResultFound):
            raise NotFoundError("Resource")
        else:
            raise ServiceException(f"Database error during {operation}: {str(error)}", "DATABASE_ERROR")
    
    def log_operation(self, operation: str, details: Dict[str, Any] = None) -> None:
        """Log service operation (placeholder for actual logging)."""
        # In a real implementation, this would use proper logging
        print(f"Service operation: {operation}, details: {details}")


class CRUDService(BaseService, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """Generic CRUD service providing common database operations."""
    
    def __init__(self, model: Type[ModelType], settings: CoreSettings = None):
        super().__init__(settings)
        self.model = model
    
    def get(self, id: Union[UUID, str, int]) -> Optional[ModelType]:
        """Get a single record by ID."""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            self.handle_db_error(e, "get record")
    
    async def async_get(self, id: Union[UUID, str, int]) -> Optional[ModelType]:
        """Async get a single record by ID."""
        try:
            result = await self.async_db.execute(
                select(self.model).where(self.model.id == id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            self.handle_db_error(e, "async get record")
    
    def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """Get a single record by field value."""
        try:
            return self.db.query(self.model).filter(getattr(self.model, field) == value).first()
        except Exception as e:
            self.handle_db_error(e, f"get record by {field}")
    
    def get_multi(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        order_by: str = None,
        order_desc: bool = False
    ) -> List[ModelType]:
        """Get multiple records with pagination and filtering."""
        try:
            query = self.db.query(self.model)
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        if isinstance(value, list):
                            query = query.filter(getattr(self.model, field).in_(value))
                        else:
                            query = query.filter(getattr(self.model, field) == value)
            
            # Apply ordering
            if order_by and hasattr(self.model, order_by):
                order_field = getattr(self.model, order_by)
                if order_desc:
                    query = query.order_by(order_field.desc())
                else:
                    query = query.order_by(order_field)
            
            # Apply pagination
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            self.handle_db_error(e, "get multiple records")
    
    def count(self, filters: Dict[str, Any] = None) -> int:
        """Count records with optional filtering."""
        try:
            query = self.db.query(func.count(self.model.id))
            
            # Apply filters
            if filters:
                for field, value in filters.items():
                    if hasattr(self.model, field):
                        if isinstance(value, list):
                            query = query.filter(getattr(self.model, field).in_(value))
                        else:
                            query = query.filter(getattr(self.model, field) == value)
            
            return query.scalar()
        except Exception as e:
            self.handle_db_error(e, "count records")
    
    def create(self, obj_in: CreateSchemaType, commit: bool = True) -> ModelType:
        """Create a new record."""
        try:
            # Convert Pydantic model to dict
            if isinstance(obj_in, BaseModel):
                obj_data = obj_in.dict(exclude_unset=True)
            else:
                obj_data = obj_in
            
            # Create model instance
            db_obj = self.model(**obj_data)
            
            # Add to session
            self.db.add(db_obj)
            
            if commit:
                self.db.commit()
                self.db.refresh(db_obj)
            
            self.log_operation("create", {"model": self.model.__name__, "id": db_obj.id})
            return db_obj
        except Exception as e:
            if commit:
                self.db.rollback()
            self.handle_db_error(e, "create record")
    
    async def async_create(self, obj_in: CreateSchemaType, commit: bool = True) -> ModelType:
        """Async create a new record."""
        try:
            # Convert Pydantic model to dict
            if isinstance(obj_in, BaseModel):
                obj_data = obj_in.dict(exclude_unset=True)
            else:
                obj_data = obj_in
            
            # Create model instance
            db_obj = self.model(**obj_data)
            
            # Add to session
            self.async_db.add(db_obj)
            
            if commit:
                await self.async_db.commit()
                await self.async_db.refresh(db_obj)
            
            self.log_operation("async_create", {"model": self.model.__name__, "id": db_obj.id})
            return db_obj
        except Exception as e:
            if commit:
                await self.async_db.rollback()
            self.handle_db_error(e, "async create record")
    
    def update(
        self,
        id: Union[UUID, str, int],
        obj_in: UpdateSchemaType,
        commit: bool = True
    ) -> Optional[ModelType]:
        """Update an existing record."""
        try:
            # Get existing record
            db_obj = self.get(id)
            if not db_obj:
                raise NotFoundError(self.model.__name__, id)
            
            # Convert Pydantic model to dict
            if isinstance(obj_in, BaseModel):
                update_data = obj_in.dict(exclude_unset=True)
            else:
                update_data = obj_in
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            # Update timestamp if available
            if hasattr(db_obj, 'updated_at'):
                db_obj.updated_at = datetime.utcnow()
            
            if commit:
                self.db.commit()
                self.db.refresh(db_obj)
            
            self.log_operation("update", {"model": self.model.__name__, "id": id})
            return db_obj
        except Exception as e:
            if commit:
                self.db.rollback()
            self.handle_db_error(e, "update record")
    
    def delete(self, id: Union[UUID, str, int], soft_delete: bool = True, commit: bool = True) -> bool:
        """Delete a record (soft delete by default)."""
        try:
            # Get existing record
            db_obj = self.get(id)
            if not db_obj:
                raise NotFoundError(self.model.__name__, id)
            
            if soft_delete and hasattr(db_obj, 'is_deleted'):
                # Soft delete
                db_obj.is_deleted = True
                if hasattr(db_obj, 'deleted_at'):
                    db_obj.deleted_at = datetime.utcnow()
            else:
                # Hard delete
                self.db.delete(db_obj)
            
            if commit:
                self.db.commit()
            
            self.log_operation("delete", {
                "model": self.model.__name__,
                "id": id,
                "soft_delete": soft_delete
            })
            return True
        except Exception as e:
            if commit:
                self.db.rollback()
            self.handle_db_error(e, "delete record")
    
    def bulk_create(self, objects: List[CreateSchemaType], commit: bool = True) -> List[ModelType]:
        """Create multiple records in bulk."""
        try:
            db_objects = []
            for obj_in in objects:
                # Convert Pydantic model to dict
                if isinstance(obj_in, BaseModel):
                    obj_data = obj_in.dict(exclude_unset=True)
                else:
                    obj_data = obj_in
                
                db_obj = self.model(**obj_data)
                db_objects.append(db_obj)
            
            # Add all to session
            self.db.add_all(db_objects)
            
            if commit:
                self.db.commit()
                for db_obj in db_objects:
                    self.db.refresh(db_obj)
            
            self.log_operation("bulk_create", {
                "model": self.model.__name__,
                "count": len(db_objects)
            })
            return db_objects
        except Exception as e:
            if commit:
                self.db.rollback()
            self.handle_db_error(e, "bulk create records")
    
    def bulk_update(
        self,
        filters: Dict[str, Any],
        update_data: Dict[str, Any],
        commit: bool = True
    ) -> int:
        """Update multiple records in bulk."""
        try:
            query = self.db.query(self.model)
            
            # Apply filters
            for field, value in filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
            
            # Add timestamp if available
            if hasattr(self.model, 'updated_at'):
                update_data['updated_at'] = datetime.utcnow()
            
            # Execute bulk update
            result = query.update(update_data)
            
            if commit:
                self.db.commit()
            
            self.log_operation("bulk_update", {
                "model": self.model.__name__,
                "filters": filters,
                "updated_count": result
            })
            return result
        except Exception as e:
            if commit:
                self.db.rollback()
            self.handle_db_error(e, "bulk update records")
    
    def exists(self, id: Union[UUID, str, int]) -> bool:
        """Check if a record exists."""
        try:
            return self.db.query(self.model.id).filter(self.model.id == id).first() is not None
        except Exception as e:
            self.handle_db_error(e, "check record existence")
    
    def search(
        self,
        search_term: str,
        search_fields: List[str],
        skip: int = 0,
        limit: int = 100
    ) -> List[ModelType]:
        """Search records by term in specified fields."""
        try:
            query = self.db.query(self.model)
            
            # Build search conditions
            search_conditions = []
            for field in search_fields:
                if hasattr(self.model, field):
                    field_attr = getattr(self.model, field)
                    search_conditions.append(field_attr.ilike(f"%{search_term}%"))
            
            if search_conditions:
                query = query.filter(or_(*search_conditions))
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            self.handle_db_error(e, "search records")