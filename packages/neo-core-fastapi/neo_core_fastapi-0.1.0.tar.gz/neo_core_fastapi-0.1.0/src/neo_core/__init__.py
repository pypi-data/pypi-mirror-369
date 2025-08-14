"""Neo Core FastAPI - Core library for FastAPI applications.

This package provides shared models, services, utilities, and database management
for FastAPI dynamic module loader systems.
"""

__version__ = "0.1.0"
__author__ = "Neo Core Team"
__email__ = "dev@neo-core.com"
__license__ = "MIT"

from .config import CoreSettings
from .database import DatabaseManager
from .auth import AuthManager

# Core models
from .models import (
    User,
    Role,
    Permission,
    Application,
    AuditLog,
)

# Core services
from .services import (
    BaseService,
    UserService,
    RoleService,
    PermissionService,
    ApplicationService,
    AuditService,
)

# Dependencies
from .dependencies import (
    get_current_user,
    get_current_active_user,
    require_permission,
    get_db_session,
)

# Utilities
from .utils import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token,
    validate_email,
    validate_phone,
)

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    "__license__",
    
    # Core components
    "CoreSettings",
    "DatabaseManager",
    "AuthManager",
    
    # Models
    "User",
    "Role",
    "Permission",
    "Application",
    "AuditLog",
    
    # Services
    "BaseService",
    "UserService",
    "RoleService",
    "PermissionService",
    "ApplicationService",
    "AuditService",
    
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "require_permission",
    "get_db_session",
    
    # Utilities
    "hash_password",
    "verify_password",
    "create_access_token",
    "decode_token",
    "validate_email",
    "validate_phone",
]