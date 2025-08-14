"""Application models for managing applications and modules."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ..database.base import BaseModel
from ..database.mixins import TimestampMixin, SoftDeleteMixin, AuditMixin, StatusMixin


class ApplicationStatus(str, Enum):
    """Application status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    DEPRECATED = "deprecated"
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class ApplicationType(str, Enum):
    """Application type enumeration."""
    WEB = "web"
    API = "api"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    SERVICE = "service"
    MICROSERVICE = "microservice"
    PLUGIN = "plugin"
    EXTENSION = "extension"


class ModuleStatus(str, Enum):
    """Module status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOADING = "loading"
    ERROR = "error"
    DISABLED = "disabled"
    UPDATING = "updating"


class ModuleType(str, Enum):
    """Module type enumeration."""
    CORE = "core"
    FEATURE = "feature"
    PLUGIN = "plugin"
    EXTENSION = "extension"
    THEME = "theme"
    WIDGET = "widget"
    SERVICE = "service"
    MIDDLEWARE = "middleware"


class Application(BaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin, StatusMixin):
    """Application model for managing applications."""
    
    __tablename__ = "application"
    
    # Basic information
    name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Application name (unique)"
    )
    
    display_name = Column(
        String(200),
        nullable=True,
        comment="Human-readable application name"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Application description"
    )
    
    # Application properties
    app_type = Column(
        String(20),
        default=ApplicationType.WEB,
        nullable=False,
        comment="Application type"
    )
    
    version = Column(
        String(50),
        default="1.0.0",
        nullable=False,
        comment="Application version"
    )
    
    # URLs and endpoints
    base_url = Column(
        String(500),
        nullable=True,
        comment="Application base URL"
    )
    
    api_url = Column(
        String(500),
        nullable=True,
        comment="API base URL"
    )
    
    admin_url = Column(
        String(500),
        nullable=True,
        comment="Admin interface URL"
    )
    
    # Security and access
    is_public = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Public access allowed"
    )
    
    requires_authentication = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Authentication required"
    )
    
    allowed_origins = Column(
        JSONB,
        nullable=True,
        comment="Allowed CORS origins"
    )
    
    # Configuration
    config = Column(
        JSONB,
        nullable=True,
        comment="Application configuration"
    )
    
    environment_config = Column(
        JSONB,
        nullable=True,
        comment="Environment-specific configuration"
    )
    
    # Resources and limits
    max_users = Column(
        Integer,
        nullable=True,
        comment="Maximum concurrent users"
    )
    
    max_requests_per_minute = Column(
        Integer,
        nullable=True,
        comment="Rate limit per minute"
    )
    
    storage_quota_mb = Column(
        Integer,
        nullable=True,
        comment="Storage quota in MB"
    )
    
    # Monitoring and health
    health_check_url = Column(
        String(500),
        nullable=True,
        comment="Health check endpoint"
    )
    
    last_health_check = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last health check timestamp"
    )
    
    health_status = Column(
        String(20),
        default="unknown",
        nullable=False,
        comment="Current health status"
    )
    
    uptime_percentage = Column(
        Float,
        default=0.0,
        nullable=False,
        comment="Uptime percentage"
    )
    
    # Deployment information
    deployment_environment = Column(
        String(50),
        nullable=True,
        comment="Deployment environment"
    )
    
    deployed_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Last deployment timestamp"
    )
    
    deployed_by = Column(
        UUID(as_uuid=True),
        nullable=True,
        comment="User who deployed the application"
    )
    
    # Additional metadata
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional application metadata"
    )
    
    tags = Column(
        String(500),
        nullable=True,
        comment="Comma-separated tags"
    )
    
    # Relationships
    modules = relationship(
        "ApplicationModule",
        back_populates="application",
        cascade="all, delete-orphan"
    )
    
    configs = relationship(
        "ApplicationConfig",
        back_populates="application",
        cascade="all, delete-orphan"
    )
    
    roles = relationship(
        "Role",
        back_populates="application"
    )
    
    permissions = relationship(
        "Permission",
        back_populates="application"
    )
    
    permission_groups = relationship(
        "PermissionGroup",
        back_populates="application"
    )
    
    def __repr__(self) -> str:
        return f"<Application(id={self.id}, name={self.name}, version={self.version})>"
    
    @property
    def is_healthy(self) -> bool:
        """Check if application is healthy."""
        return self.health_status in ["healthy", "ok", "up"]
    
    @property
    def active_modules_count(self) -> int:
        """Get count of active modules."""
        return len([m for m in self.modules if m.status == ModuleStatus.ACTIVE])
    
    @property
    def total_modules_count(self) -> int:
        """Get total count of modules."""
        return len(self.modules)
    
    def get_config_value(self, key: str, default=None, environment: str = None):
        """Get configuration value."""
        # First check environment-specific config
        if environment and self.environment_config:
            env_config = self.environment_config.get(environment, {})
            if key in env_config:
                return env_config[key]
        
        # Then check general config
        if self.config and key in self.config:
            return self.config[key]
        
        return default
    
    def set_config_value(self, key: str, value: Any, environment: str = None) -> None:
        """Set configuration value."""
        if environment:
            if self.environment_config is None:
                self.environment_config = {}
            if environment not in self.environment_config:
                self.environment_config[environment] = {}
            self.environment_config[environment][key] = value
        else:
            if self.config is None:
                self.config = {}
            self.config[key] = value
    
    def update_health_status(self, status: str, check_time: datetime = None) -> None:
        """Update health status."""
        self.health_status = status
        self.last_health_check = check_time or datetime.utcnow()
    
    def get_module_by_name(self, module_name: str) -> Optional['ApplicationModule']:
        """Get module by name."""
        for module in self.modules:
            if module.name == module_name:
                return module
        return None
    
    def add_module(self, module_name: str, module_path: str, **kwargs) -> 'ApplicationModule':
        """Add new module to application."""
        module = ApplicationModule(
            application_id=self.id,
            name=module_name,
            path=module_path,
            **kwargs
        )
        self.modules.append(module)
        return module
    
    def remove_module(self, module_name: str) -> bool:
        """Remove module from application."""
        module = self.get_module_by_name(module_name)
        if module:
            self.modules.remove(module)
            return True
        return False


class ApplicationModule(BaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Application module model for managing dynamic modules."""
    
    __tablename__ = "application_module"
    
    # Foreign key
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("application.id"),
        nullable=False,
        comment="Application ID"
    )
    
    # Basic information
    name = Column(
        String(100),
        nullable=False,
        index=True,
        comment="Module name"
    )
    
    display_name = Column(
        String(200),
        nullable=True,
        comment="Human-readable module name"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Module description"
    )
    
    # Module properties
    module_type = Column(
        String(20),
        default=ModuleType.FEATURE,
        nullable=False,
        comment="Module type"
    )
    
    status = Column(
        String(20),
        default=ModuleStatus.INACTIVE,
        nullable=False,
        comment="Module status"
    )
    
    version = Column(
        String(50),
        default="1.0.0",
        nullable=False,
        comment="Module version"
    )
    
    # File and path information
    path = Column(
        String(500),
        nullable=False,
        comment="Module file path"
    )
    
    entry_point = Column(
        String(200),
        nullable=True,
        comment="Module entry point function"
    )
    
    # Dependencies
    dependencies = Column(
        JSONB,
        nullable=True,
        comment="Module dependencies"
    )
    
    requirements = Column(
        JSONB,
        nullable=True,
        comment="Module requirements"
    )
    
    # Loading and execution
    load_order = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Module loading order"
    )
    
    auto_load = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Auto-load on application start"
    )
    
    lazy_load = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Lazy loading enabled"
    )
    
    # Runtime information
    loaded_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Module load timestamp"
    )
    
    last_error = Column(
        Text,
        nullable=True,
        comment="Last error message"
    )
    
    error_count = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Error count"
    )
    
    # Performance metrics
    load_time_ms = Column(
        Integer,
        nullable=True,
        comment="Load time in milliseconds"
    )
    
    memory_usage_mb = Column(
        Float,
        nullable=True,
        comment="Memory usage in MB"
    )
    
    # Configuration
    config = Column(
        JSONB,
        nullable=True,
        comment="Module configuration"
    )
    
    # Additional metadata
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional module metadata"
    )
    
    # Relationships
    application = relationship(
        "Application",
        back_populates="modules"
    )
    
    def __repr__(self) -> str:
        return f"<ApplicationModule(id={self.id}, name={self.name}, status={self.status})>"
    
    @property
    def is_loaded(self) -> bool:
        """Check if module is loaded."""
        return self.status == ModuleStatus.ACTIVE and self.loaded_at is not None
    
    @property
    def has_errors(self) -> bool:
        """Check if module has errors."""
        return self.status == ModuleStatus.ERROR or self.error_count > 0
    
    def mark_as_loaded(self, load_time_ms: int = None) -> None:
        """Mark module as loaded."""
        self.status = ModuleStatus.ACTIVE
        self.loaded_at = datetime.utcnow()
        if load_time_ms is not None:
            self.load_time_ms = load_time_ms
        self.last_error = None
    
    def mark_as_error(self, error_message: str) -> None:
        """Mark module as having error."""
        self.status = ModuleStatus.ERROR
        self.last_error = error_message
        self.error_count += 1
    
    def reset_errors(self) -> None:
        """Reset error state."""
        self.last_error = None
        self.error_count = 0
        if self.status == ModuleStatus.ERROR:
            self.status = ModuleStatus.INACTIVE
    
    def get_config_value(self, key: str, default=None):
        """Get module configuration value."""
        if self.config and key in self.config:
            return self.config[key]
        return default
    
    def set_config_value(self, key: str, value: Any) -> None:
        """Set module configuration value."""
        if self.config is None:
            self.config = {}
        self.config[key] = value


class ApplicationConfig(BaseModel, TimestampMixin, AuditMixin):
    """Application configuration model for storing key-value configurations."""
    
    __tablename__ = "application_config"
    
    # Foreign key
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("application.id"),
        nullable=False,
        comment="Application ID"
    )
    
    # Configuration key-value
    key = Column(
        String(200),
        nullable=False,
        index=True,
        comment="Configuration key"
    )
    
    value = Column(
        Text,
        nullable=True,
        comment="Configuration value"
    )
    
    # Configuration properties
    data_type = Column(
        String(20),
        default="string",
        nullable=False,
        comment="Value data type"
    )
    
    is_encrypted = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Value is encrypted"
    )
    
    is_secret = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Value is secret (sensitive)"
    )
    
    # Environment and scope
    environment = Column(
        String(50),
        nullable=True,
        comment="Environment scope"
    )
    
    scope = Column(
        String(50),
        default="application",
        nullable=False,
        comment="Configuration scope"
    )
    
    # Validation and constraints
    validation_rules = Column(
        JSONB,
        nullable=True,
        comment="Validation rules for the value"
    )
    
    default_value = Column(
        Text,
        nullable=True,
        comment="Default value"
    )
    
    # Additional metadata
    description = Column(
        Text,
        nullable=True,
        comment="Configuration description"
    )
    
    category = Column(
        String(100),
        nullable=True,
        comment="Configuration category"
    )
    
    # Relationships
    application = relationship(
        "Application",
        back_populates="configs"
    )
    
    def __repr__(self) -> str:
        return f"<ApplicationConfig(id={self.id}, key={self.key}, app_id={self.application_id})>"
    
    def get_typed_value(self):
        """Get value converted to appropriate type."""
        if self.value is None:
            return None
        
        if self.data_type == "boolean":
            return self.value.lower() in ("true", "1", "yes", "on")
        elif self.data_type == "integer":
            try:
                return int(self.value)
            except ValueError:
                return None
        elif self.data_type == "float":
            try:
                return float(self.value)
            except ValueError:
                return None
        elif self.data_type == "json":
            try:
                import json
                return json.loads(self.value)
            except (json.JSONDecodeError, TypeError):
                return None
        else:
            return self.value
    
    def set_typed_value(self, value: Any) -> None:
        """Set value with automatic type detection."""
        if value is None:
            self.value = None
            self.data_type = "string"
        elif isinstance(value, bool):
            self.value = str(value).lower()
            self.data_type = "boolean"
        elif isinstance(value, int):
            self.value = str(value)
            self.data_type = "integer"
        elif isinstance(value, float):
            self.value = str(value)
            self.data_type = "float"
        elif isinstance(value, (dict, list)):
            import json
            self.value = json.dumps(value)
            self.data_type = "json"
        else:
            self.value = str(value)
            self.data_type = "string"
    
    def validate_value(self) -> tuple[bool, str]:
        """Validate configuration value against rules."""
        if not self.validation_rules:
            return True, "OK"
        
        # Implement validation logic based on rules
        # This is a placeholder for custom validation
        return True, "OK"