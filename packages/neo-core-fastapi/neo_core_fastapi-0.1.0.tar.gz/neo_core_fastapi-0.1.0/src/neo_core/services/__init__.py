"""Service layer for the neo-core-fastapi library."""

# Base services
from .base import BaseService, ServiceException, ValidationException, NotFoundError, DuplicateError, PermissionError
from .crud import (
    UserCRUDService,
    UserProfileCRUDService,
    UserPreferenceCRUDService,
    RoleCRUDService,
    PermissionCRUDService,
    PermissionGroupCRUDService,
    ApplicationCRUDService,
    ApplicationModuleCRUDService,
    ApplicationConfigCRUDService,
    AuditLogCRUDService,
    UserSessionCRUDService,
    NotificationCRUDService,
    FileCRUDService
)

# Authentication and authorization services
from .auth import (
    AuthenticationError,
    AuthorizationError,
    TokenExpiredError,
    InvalidTokenError,
    PasswordService,
    TokenService,
    AuthService,
    AuthorizationService
)

# User management services
from .user import (
    UserService,
    UserProfileService,
    UserPreferenceService,
    UserCreateSchema,
    UserUpdateSchema,
    UserProfileCreateSchema,
    UserProfileUpdateSchema,
    UserPreferenceCreateSchema,
    UserPreferenceUpdateSchema
)

# Role and permission services
from .role import (
    RoleService,
    PermissionService,
    PermissionGroupService,
    RoleCreateSchema,
    RoleUpdateSchema,
    PermissionCreateSchema,
    PermissionUpdateSchema,
    PermissionGroupCreateSchema,
    PermissionGroupUpdateSchema
)

# Application management services
from .application import (
    ApplicationService,
    ApplicationModuleService,
    ApplicationConfigService,
    ApplicationCreateSchema,
    ApplicationUpdateSchema,
    ApplicationModuleCreateSchema,
    ApplicationModuleUpdateSchema,
    ApplicationConfigCreateSchema,
    ApplicationConfigUpdateSchema
)

# Audit services
from .audit import (
    AuditService,
    AuditLogCreateSchema,
    AuditLogFilterSchema
)

# Session services
from .session import SessionService

# Notification services
from .notification import (
    NotificationService,
    NotificationCreateSchema,
    NotificationUpdateSchema,
    NotificationTemplateCreateSchema,
    NotificationTemplateUpdateSchema,
    UserNotificationUpdateSchema
)

# File services
from .file import (
    FileService,
    FileCreateSchema,
    FileUpdateSchema,
    FileVersionCreateSchema,
    FileShareCreateSchema,
    FileShareUpdateSchema
)

# Cache services
from .cache import (
    CacheService,
    CacheException,
    CacheKeyError,
    CacheConnectionError,
    BaseCacheService,
    MemoryCacheService,
    RedisCacheService,
    EncryptedData
)

# Email services
from .email import (
    EmailService,
    EmailException,
    EmailConfigurationError,
    EmailSendError,
    EmailTemplateError,
    EmailAttachment,
    EmailMessage,
    EmailTemplate,
    SMTPConfig
)

# Security services
from .security import (
    SecurityService,
    EncryptionService,
    HashingService,
    TokenService,
    SecurityException,
    EncryptionError,
    SignatureError,
    TokenError,
    EncryptedData,
    SignedData,
    SecurityToken
)

# Monitoring services
from .monitoring import (
    MonitoringService,
    MonitoringException,
    MetricType,
    AlertLevel,
    HealthStatus,
    Metric,
    Alert,
    HealthCheck,
    SystemMetrics,
    ApplicationMetrics,
    MetricsCollector,
    AlertManager,
    HealthCheckManager,
    SystemMonitor
)

__all__ = [
    # Base services
    "BaseService",
    "ServiceException",
    "ValidationException",
    "NotFoundError",
    "DuplicateError",
    "PermissionError",
    
    # CRUD services
    "UserCRUDService",
    "UserProfileCRUDService",
    "UserPreferenceCRUDService",
    "RoleCRUDService",
    "PermissionCRUDService",
    "PermissionGroupCRUDService",
    "ApplicationCRUDService",
    "ApplicationModuleCRUDService",
    "ApplicationConfigCRUDService",
    "AuditLogCRUDService",
    "UserSessionCRUDService",
    "NotificationCRUDService",
    "FileCRUDService",
    
    # Authentication and authorization
    "AuthenticationError",
    "AuthorizationError",
    "TokenExpiredError",
    "InvalidTokenError",
    "PasswordService",
    "TokenService",
    "AuthService",
    "AuthorizationService",
    
    # User management
    "UserService",
    "UserProfileService",
    "UserPreferenceService",
    "UserCreateSchema",
    "UserUpdateSchema",
    "UserProfileCreateSchema",
    "UserProfileUpdateSchema",
    "UserPreferenceCreateSchema",
    "UserPreferenceUpdateSchema",
    
    # Role and permission management
    "RoleService",
    "PermissionService",
    "PermissionGroupService",
    "RoleCreateSchema",
    "RoleUpdateSchema",
    "PermissionCreateSchema",
    "PermissionUpdateSchema",
    "PermissionGroupCreateSchema",
    "PermissionGroupUpdateSchema",
    
    # Application management
    "ApplicationService",
    "ApplicationModuleService",
    "ApplicationConfigService",
    "ApplicationCreateSchema",
    "ApplicationUpdateSchema",
    "ApplicationModuleCreateSchema",
    "ApplicationModuleUpdateSchema",
    "ApplicationConfigCreateSchema",
    "ApplicationConfigUpdateSchema",
    
    # Audit
    "AuditService",
    "AuditLogCreateSchema",
    "AuditLogFilterSchema",
    
    # Session management
    "SessionService",
    
    # Notification
    "NotificationService",
    "NotificationCreateSchema",
    "NotificationUpdateSchema",
    "NotificationTemplateCreateSchema",
    "NotificationTemplateUpdateSchema",
    "UserNotificationUpdateSchema",
    
    # File management
    "FileService",
    "FileCreateSchema",
    "FileUpdateSchema",
    "FileVersionCreateSchema",
    "FileShareCreateSchema",
    "FileShareUpdateSchema",
    
    # Cache
    "CacheService",
    "CacheException",
    "CacheKeyError",
    "CacheConnectionError",
    "BaseCacheService",
    "MemoryCacheService",
    "RedisCacheService",
    "EncryptedData",
    
    # Email
    "EmailService",
    "EmailException",
    "EmailConfigurationError",
    "EmailSendError",
    "EmailTemplateError",
    "EmailAttachment",
    "EmailMessage",
    "EmailTemplate",
    "SMTPConfig",
    
    # Security
    "SecurityService",
    "EncryptionService",
    "HashingService",
    "SecurityException",
    "EncryptionError",
    "SignatureError",
    "TokenError",
    "SignedData",
    "SecurityToken",
    
    # Monitoring
    "MonitoringService",
    "MonitoringException",
    "MetricType",
    "AlertLevel",
    "HealthStatus",
    "Metric",
    "Alert",
    "HealthCheck",
    "SystemMetrics",
    "ApplicationMetrics",
    "MetricsCollector",
    "AlertManager",
    "HealthCheckManager",
    "SystemMonitor",
]