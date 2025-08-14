"""Application management services."""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from pydantic import BaseModel, HttpUrl

from .base import BaseService, ServiceException, NotFoundError, ValidationException, DuplicateError
from .crud import ApplicationCRUDService, ApplicationModuleCRUDService, ApplicationConfigCRUDService
from ..models.application import Application, ApplicationModule, ApplicationConfig
from ..models.application import ApplicationStatus, ApplicationType, ModuleStatus, ModuleType
from ..config import CoreSettings


class ApplicationCreateSchema(BaseModel):
    """Schema for creating an application."""
    name: str
    code: str
    description: Optional[str] = None
    type: ApplicationType = ApplicationType.WEB
    status: ApplicationStatus = ApplicationStatus.ACTIVE
    version: str = "1.0.0"
    base_url: Optional[HttpUrl] = None
    api_url: Optional[HttpUrl] = None
    admin_url: Optional[HttpUrl] = None
    documentation_url: Optional[HttpUrl] = None
    repository_url: Optional[HttpUrl] = None
    is_public: bool = False
    is_system: bool = False
    is_default: bool = False
    config: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    priority: int = 0
    max_instances: Optional[int] = None
    health_check_url: Optional[HttpUrl] = None
    health_check_interval: int = 300
    deployment_config: Optional[Dict[str, Any]] = None


class ApplicationUpdateSchema(BaseModel):
    """Schema for updating an application."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ApplicationStatus] = None
    version: Optional[str] = None
    base_url: Optional[HttpUrl] = None
    api_url: Optional[HttpUrl] = None
    admin_url: Optional[HttpUrl] = None
    documentation_url: Optional[HttpUrl] = None
    repository_url: Optional[HttpUrl] = None
    is_public: Optional[bool] = None
    is_default: Optional[bool] = None
    config: Optional[Dict[str, Any]] = None
    resources: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    priority: Optional[int] = None
    max_instances: Optional[int] = None
    health_check_url: Optional[HttpUrl] = None
    health_check_interval: Optional[int] = None
    deployment_config: Optional[Dict[str, Any]] = None


class ApplicationModuleCreateSchema(BaseModel):
    """Schema for creating an application module."""
    name: str
    code: str
    description: Optional[str] = None
    type: ModuleType = ModuleType.FEATURE
    status: ModuleStatus = ModuleStatus.ACTIVE
    version: str = "1.0.0"
    application_id: UUID
    parent_module_id: Optional[UUID] = None
    entry_point: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    resources: Optional[Dict[str, Any]] = None
    is_core: bool = False
    is_optional: bool = True
    load_order: int = 0
    auto_load: bool = True
    health_check_enabled: bool = False
    health_check_interval: int = 300


class ApplicationModuleUpdateSchema(BaseModel):
    """Schema for updating an application module."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ModuleStatus] = None
    version: Optional[str] = None
    parent_module_id: Optional[UUID] = None
    entry_point: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    dependencies: Optional[List[str]] = None
    resources: Optional[Dict[str, Any]] = None
    is_optional: Optional[bool] = None
    load_order: Optional[int] = None
    auto_load: Optional[bool] = None
    health_check_enabled: Optional[bool] = None
    health_check_interval: Optional[int] = None


class ApplicationConfigCreateSchema(BaseModel):
    """Schema for creating an application configuration."""
    key: str
    value: Any
    description: Optional[str] = None
    application_id: UUID
    module_id: Optional[UUID] = None
    category: str = "general"
    data_type: str = "string"
    is_secret: bool = False
    is_required: bool = False
    is_system: bool = False
    default_value: Optional[Any] = None
    validation_rules: Optional[Dict[str, Any]] = None
    environment: str = "production"


class ApplicationConfigUpdateSchema(BaseModel):
    """Schema for updating an application configuration."""
    value: Optional[Any] = None
    description: Optional[str] = None
    category: Optional[str] = None
    data_type: Optional[str] = None
    is_secret: Optional[bool] = None
    is_required: Optional[bool] = None
    default_value: Optional[Any] = None
    validation_rules: Optional[Dict[str, Any]] = None
    environment: Optional[str] = None


class ApplicationService(BaseService):
    """Service for application management."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        self.app_crud = ApplicationCRUDService(settings)
        self.module_crud = ApplicationModuleCRUDService(settings)
        self.config_crud = ApplicationConfigCRUDService(settings)
    
    def create_application(self, app_data: ApplicationCreateSchema) -> Application:
        """Create a new application."""
        try:
            # Validate input
            app_data = self.validate_input(app_data, ApplicationCreateSchema)
            
            # Check if application name already exists
            existing_app = self.app_crud.get_by_name(app_data.name)
            if existing_app:
                raise DuplicateError("Application", "name", app_data.name)
            
            # Check if application code already exists
            existing_app = self.app_crud.get_by_code(app_data.code)
            if existing_app:
                raise DuplicateError("Application", "code", app_data.code)
            
            # Create application data
            create_data = {
                "id": uuid4(),
                "name": app_data.name,
                "code": app_data.code,
                "description": app_data.description,
                "type": app_data.type,
                "status": app_data.status,
                "version": app_data.version,
                "base_url": str(app_data.base_url) if app_data.base_url else None,
                "api_url": str(app_data.api_url) if app_data.api_url else None,
                "admin_url": str(app_data.admin_url) if app_data.admin_url else None,
                "documentation_url": str(app_data.documentation_url) if app_data.documentation_url else None,
                "repository_url": str(app_data.repository_url) if app_data.repository_url else None,
                "is_public": app_data.is_public,
                "is_system": app_data.is_system,
                "is_default": app_data.is_default,
                "config": app_data.config or {},
                "resources": app_data.resources or {},
                "dependencies": app_data.dependencies or [],
                "tags": app_data.tags or [],
                "priority": app_data.priority,
                "max_instances": app_data.max_instances,
                "health_check_url": str(app_data.health_check_url) if app_data.health_check_url else None,
                "health_check_interval": app_data.health_check_interval,
                "deployment_config": app_data.deployment_config or {},
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create application
            application = self.app_crud.create(create_data)
            
            self.log_operation("create_application", {
                "application_id": application.id,
                "name": application.name,
                "code": application.code
            })
            
            return application
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create application")
    
    def get_application(self, app_id: UUID, include_modules: bool = False) -> Optional[Application]:
        """Get an application by ID with optional modules."""
        try:
            application = self.app_crud.get(app_id)
            if not application:
                return None
            
            # Load modules if requested
            if include_modules:
                application.modules = self.module_crud.get_modules_by_application(app_id)
            
            return application
        except Exception as e:
            self.handle_db_error(e, "get application")
    
    def get_application_by_code(self, code: str) -> Optional[Application]:
        """Get an application by code."""
        return self.app_crud.get_by_code(code)
    
    def update_application(self, app_id: UUID, app_data: ApplicationUpdateSchema) -> Application:
        """Update an application."""
        try:
            # Validate input
            app_data = self.validate_input(app_data, ApplicationUpdateSchema)
            
            # Get existing application
            application = self.app_crud.get(app_id)
            if not application:
                raise NotFoundError("Application", app_id)
            
            # Check if it's a system application and prevent certain updates
            if application.is_system and app_data.name:
                raise ValidationException("Cannot change name of system application")
            
            # Check for name conflicts
            if app_data.name and app_data.name != application.name:
                existing_app = self.app_crud.get_by_name(app_data.name)
                if existing_app and existing_app.id != app_id:
                    raise DuplicateError("Application", "name", app_data.name)
            
            # Convert URLs to strings
            update_data = app_data.dict(exclude_unset=True)
            for url_field in ["base_url", "api_url", "admin_url", "documentation_url", "repository_url", "health_check_url"]:
                if url_field in update_data and update_data[url_field] is not None:
                    update_data[url_field] = str(update_data[url_field])
            
            # Update application
            updated_application = self.app_crud.update(app_id, update_data)
            
            self.log_operation("update_application", {
                "application_id": app_id,
                "updated_fields": list(update_data.keys())
            })
            
            return updated_application
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "update application")
    
    def delete_application(self, app_id: UUID, soft_delete: bool = True) -> bool:
        """Delete an application."""
        try:
            application = self.app_crud.get(app_id)
            if not application:
                raise NotFoundError("Application", app_id)
            
            # Prevent deletion of system applications
            if application.is_system:
                raise ValidationException("Cannot delete system application")
            
            # Check if application has active modules
            active_modules = self.module_crud.get_multi(filters={
                "application_id": app_id,
                "status": ModuleStatus.ACTIVE
            })
            if active_modules:
                raise ValidationException("Cannot delete application with active modules")
            
            # Perform deletion
            result = self.app_crud.delete(app_id, soft_delete=soft_delete)
            
            self.log_operation("delete_application", {
                "application_id": app_id,
                "soft_delete": soft_delete
            })
            
            return result
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "delete application")
    
    def list_applications(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        order_by: str = "name",
        order_desc: bool = False
    ) -> List[Application]:
        """List applications with filtering and pagination."""
        return self.app_crud.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=order_by,
            order_desc=order_desc
        )
    
    def get_public_applications(self) -> List[Application]:
        """Get all public applications."""
        return self.app_crud.get_multi(filters={"is_public": True, "status": ApplicationStatus.ACTIVE})
    
    def check_application_health(self, app_id: UUID) -> Dict[str, Any]:
        """Check application health status."""
        try:
            application = self.app_crud.get(app_id)
            if not application:
                raise NotFoundError("Application", app_id)
            
            health_status = {
                "application_id": app_id,
                "name": application.name,
                "status": application.status,
                "version": application.version,
                "is_healthy": application.status == ApplicationStatus.ACTIVE,
                "last_checked": datetime.utcnow(),
                "modules": []
            }
            
            # Check module health
            modules = self.module_crud.get_modules_by_application(app_id)
            for module in modules:
                module_health = {
                    "module_id": module.id,
                    "name": module.name,
                    "status": module.status,
                    "version": module.version,
                    "is_healthy": module.status == ModuleStatus.ACTIVE
                }
                health_status["modules"].append(module_health)
            
            # Update last health check time
            self.app_crud.update(app_id, {"last_health_check": datetime.utcnow()})
            
            return health_status
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "check application health")


class ApplicationModuleService(BaseService):
    """Service for application module management."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        self.module_crud = ApplicationModuleCRUDService(settings)
        self.app_crud = ApplicationCRUDService(settings)
    
    def create_module(self, module_data: ApplicationModuleCreateSchema) -> ApplicationModule:
        """Create a new application module."""
        try:
            # Validate input
            module_data = self.validate_input(module_data, ApplicationModuleCreateSchema)
            
            # Check if application exists
            application = self.app_crud.get(module_data.application_id)
            if not application:
                raise NotFoundError("Application", module_data.application_id)
            
            # Check if module code already exists in the application
            existing_module = self.module_crud.get_by_code_and_application(
                module_data.code, module_data.application_id
            )
            if existing_module:
                raise DuplicateError("Module", "code", module_data.code)
            
            # Validate parent module if specified
            if module_data.parent_module_id:
                parent_module = self.module_crud.get(module_data.parent_module_id)
                if not parent_module:
                    raise NotFoundError("Parent Module", module_data.parent_module_id)
                if parent_module.application_id != module_data.application_id:
                    raise ValidationException("Parent module must belong to the same application")
                if not parent_module.is_active:
                    raise ValidationException("Parent module is not active")
            
            # Create module data
            create_data = {
                "id": uuid4(),
                "name": module_data.name,
                "code": module_data.code,
                "description": module_data.description,
                "type": module_data.type,
                "status": module_data.status,
                "version": module_data.version,
                "application_id": module_data.application_id,
                "parent_module_id": module_data.parent_module_id,
                "entry_point": module_data.entry_point,
                "config": module_data.config or {},
                "dependencies": module_data.dependencies or [],
                "resources": module_data.resources or {},
                "is_core": module_data.is_core,
                "is_optional": module_data.is_optional,
                "load_order": module_data.load_order,
                "auto_load": module_data.auto_load,
                "health_check_enabled": module_data.health_check_enabled,
                "health_check_interval": module_data.health_check_interval,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create module
            module = self.module_crud.create(create_data)
            
            self.log_operation("create_module", {
                "module_id": module.id,
                "name": module.name,
                "code": module.code,
                "application_id": module.application_id
            })
            
            return module
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create module")
    
    def get_module(self, module_id: UUID) -> Optional[ApplicationModule]:
        """Get a module by ID."""
        return self.module_crud.get(module_id)
    
    def get_module_by_code(self, code: str, application_id: UUID) -> Optional[ApplicationModule]:
        """Get a module by code and application."""
        return self.module_crud.get_by_code_and_application(code, application_id)
    
    def update_module(self, module_id: UUID, module_data: ApplicationModuleUpdateSchema) -> ApplicationModule:
        """Update a module."""
        try:
            # Validate input
            module_data = self.validate_input(module_data, ApplicationModuleUpdateSchema)
            
            # Get existing module
            module = self.module_crud.get(module_id)
            if not module:
                raise NotFoundError("Module", module_id)
            
            # Validate parent module if specified
            if module_data.parent_module_id:
                if module_data.parent_module_id == module_id:
                    raise ValidationException("Module cannot be its own parent")
                
                parent_module = self.module_crud.get(module_data.parent_module_id)
                if not parent_module:
                    raise NotFoundError("Parent Module", module_data.parent_module_id)
                if parent_module.application_id != module.application_id:
                    raise ValidationException("Parent module must belong to the same application")
                if not parent_module.is_active:
                    raise ValidationException("Parent module is not active")
                
                # Check for circular dependency
                if self._would_create_circular_dependency(module_id, module_data.parent_module_id):
                    raise ValidationException("Would create circular dependency in module hierarchy")
            
            # Update module data
            update_data = module_data.dict(exclude_unset=True)
            
            # Update module
            updated_module = self.module_crud.update(module_id, update_data)
            
            self.log_operation("update_module", {
                "module_id": module_id,
                "updated_fields": list(update_data.keys())
            })
            
            return updated_module
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "update module")
    
    def delete_module(self, module_id: UUID, soft_delete: bool = True) -> bool:
        """Delete a module."""
        try:
            module = self.module_crud.get(module_id)
            if not module:
                raise NotFoundError("Module", module_id)
            
            # Prevent deletion of core modules
            if module.is_core:
                raise ValidationException("Cannot delete core module")
            
            # Check if module has child modules
            child_modules = self.module_crud.get_multi(filters={"parent_module_id": module_id})
            if child_modules:
                raise ValidationException("Cannot delete module with child modules")
            
            # Perform deletion
            result = self.module_crud.delete(module_id, soft_delete=soft_delete)
            
            self.log_operation("delete_module", {
                "module_id": module_id,
                "soft_delete": soft_delete
            })
            
            return result
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "delete module")
    
    def list_modules(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        order_by: str = "load_order",
        order_desc: bool = False
    ) -> List[ApplicationModule]:
        """List modules with filtering and pagination."""
        return self.module_crud.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=order_by,
            order_desc=order_desc
        )
    
    def get_modules_by_application(self, application_id: UUID) -> List[ApplicationModule]:
        """Get modules by application."""
        return self.module_crud.get_modules_by_application(application_id)
    
    def get_module_hierarchy(self, module_id: UUID) -> List[ApplicationModule]:
        """Get module hierarchy (parent and child modules)."""
        return self.module_crud.get_module_hierarchy(module_id)
    
    def _would_create_circular_dependency(self, module_id: UUID, parent_module_id: UUID) -> bool:
        """Check if setting parent would create circular dependency."""
        try:
            current_module_id = parent_module_id
            visited = set()
            
            while current_module_id and current_module_id not in visited:
                if current_module_id == module_id:
                    return True
                
                visited.add(current_module_id)
                parent_module = self.module_crud.get(current_module_id)
                current_module_id = parent_module.parent_module_id if parent_module else None
            
            return False
        except Exception:
            return True  # Assume circular dependency on error


class ApplicationConfigService(BaseService):
    """Service for application configuration management."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        self.config_crud = ApplicationConfigCRUDService(settings)
        self.app_crud = ApplicationCRUDService(settings)
        self.module_crud = ApplicationModuleCRUDService(settings)
    
    def create_config(self, config_data: ApplicationConfigCreateSchema) -> ApplicationConfig:
        """Create a new application configuration."""
        try:
            # Validate input
            config_data = self.validate_input(config_data, ApplicationConfigCreateSchema)
            
            # Check if application exists
            application = self.app_crud.get(config_data.application_id)
            if not application:
                raise NotFoundError("Application", config_data.application_id)
            
            # Check if module exists (if specified)
            if config_data.module_id:
                module = self.module_crud.get(config_data.module_id)
                if not module:
                    raise NotFoundError("Module", config_data.module_id)
                if module.application_id != config_data.application_id:
                    raise ValidationException("Module must belong to the specified application")
            
            # Check if config key already exists
            existing_config = self.config_crud.get_by_key_and_application(
                config_data.key, config_data.application_id, config_data.module_id, config_data.environment
            )
            if existing_config:
                raise DuplicateError("Config", "key", config_data.key)
            
            # Create config data
            create_data = {
                "id": uuid4(),
                "key": config_data.key,
                "value": config_data.value,
                "description": config_data.description,
                "application_id": config_data.application_id,
                "module_id": config_data.module_id,
                "category": config_data.category,
                "data_type": config_data.data_type,
                "is_secret": config_data.is_secret,
                "is_required": config_data.is_required,
                "is_system": config_data.is_system,
                "default_value": config_data.default_value,
                "validation_rules": config_data.validation_rules or {},
                "environment": config_data.environment,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create config
            config = self.config_crud.create(create_data)
            
            self.log_operation("create_config", {
                "config_id": config.id,
                "key": config.key,
                "application_id": config.application_id,
                "module_id": config.module_id
            })
            
            return config
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create config")
    
    def get_config(self, config_id: UUID) -> Optional[ApplicationConfig]:
        """Get a configuration by ID."""
        return self.config_crud.get(config_id)
    
    def get_config_by_key(
        self,
        key: str,
        application_id: UUID,
        module_id: Optional[UUID] = None,
        environment: str = "production"
    ) -> Optional[ApplicationConfig]:
        """Get a configuration by key."""
        return self.config_crud.get_by_key_and_application(key, application_id, module_id, environment)
    
    def update_config(self, config_id: UUID, config_data: ApplicationConfigUpdateSchema) -> ApplicationConfig:
        """Update a configuration."""
        try:
            # Validate input
            config_data = self.validate_input(config_data, ApplicationConfigUpdateSchema)
            
            # Get existing config
            config = self.config_crud.get(config_id)
            if not config:
                raise NotFoundError("Config", config_id)
            
            # Prevent updates to system configs
            if config.is_system and config_data.value is not None:
                raise ValidationException("Cannot update value of system configuration")
            
            # Update config data
            update_data = config_data.dict(exclude_unset=True)
            
            # Update config
            updated_config = self.config_crud.update(config_id, update_data)
            
            self.log_operation("update_config", {
                "config_id": config_id,
                "updated_fields": list(update_data.keys())
            })
            
            return updated_config
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "update config")
    
    def delete_config(self, config_id: UUID, soft_delete: bool = True) -> bool:
        """Delete a configuration."""
        try:
            config = self.config_crud.get(config_id)
            if not config:
                raise NotFoundError("Config", config_id)
            
            # Prevent deletion of system configs
            if config.is_system:
                raise ValidationException("Cannot delete system configuration")
            
            # Prevent deletion of required configs
            if config.is_required:
                raise ValidationException("Cannot delete required configuration")
            
            # Perform deletion
            result = self.config_crud.delete(config_id, soft_delete=soft_delete)
            
            self.log_operation("delete_config", {
                "config_id": config_id,
                "soft_delete": soft_delete
            })
            
            return result
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "delete config")
    
    def list_configs(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        order_by: str = "key",
        order_desc: bool = False
    ) -> List[ApplicationConfig]:
        """List configurations with filtering and pagination."""
        return self.config_crud.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=order_by,
            order_desc=order_desc
        )
    
    def get_configs_by_application(
        self,
        application_id: UUID,
        environment: str = "production",
        include_secrets: bool = False
    ) -> List[ApplicationConfig]:
        """Get configurations by application."""
        filters = {
            "application_id": application_id,
            "environment": environment
        }
        
        if not include_secrets:
            filters["is_secret"] = False
        
        return self.config_crud.get_multi(filters=filters)
    
    def get_configs_by_module(
        self,
        module_id: UUID,
        environment: str = "production",
        include_secrets: bool = False
    ) -> List[ApplicationConfig]:
        """Get configurations by module."""
        filters = {
            "module_id": module_id,
            "environment": environment
        }
        
        if not include_secrets:
            filters["is_secret"] = False
        
        return self.config_crud.get_multi(filters=filters)
    
    def get_config_value(
        self,
        key: str,
        application_id: UUID,
        module_id: Optional[UUID] = None,
        environment: str = "production",
        default: Any = None
    ) -> Any:
        """Get configuration value by key."""
        config = self.get_config_by_key(key, application_id, module_id, environment)
        if config:
            return config.value
        return default
    
    def set_config_value(
        self,
        key: str,
        value: Any,
        application_id: UUID,
        module_id: Optional[UUID] = None,
        environment: str = "production"
    ) -> ApplicationConfig:
        """Set configuration value by key."""
        config = self.get_config_by_key(key, application_id, module_id, environment)
        if config:
            return self.update_config(config.id, ApplicationConfigUpdateSchema(value=value))
        else:
            # Create new config
            return self.create_config(ApplicationConfigCreateSchema(
                key=key,
                value=value,
                application_id=application_id,
                module_id=module_id,
                environment=environment
            ))