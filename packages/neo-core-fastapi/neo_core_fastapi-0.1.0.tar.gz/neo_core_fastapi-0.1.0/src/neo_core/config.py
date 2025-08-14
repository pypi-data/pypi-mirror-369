"""Core configuration settings for Neo Core FastAPI."""

from typing import Optional, List, Any, Dict
from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class CoreSettings(BaseSettings):
    """Core application settings."""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Application settings
    app_name: str = Field(default="Neo Core FastAPI", description="Application name")
    app_version: str = Field(default="0.1.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment name")
    
    # Security settings
    secret_key: str = Field(..., description="Secret key for JWT tokens")
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(
        default=30, description="Access token expiration in minutes"
    )
    refresh_token_expire_days: int = Field(
        default=7, description="Refresh token expiration in days"
    )
    
    # Database settings
    database_url: str = Field(..., description="Database connection URL")
    database_echo: bool = Field(default=False, description="SQLAlchemy echo mode")
    database_pool_size: int = Field(default=10, description="Database connection pool size")
    database_max_overflow: int = Field(default=20, description="Database max overflow")
    database_pool_timeout: int = Field(default=30, description="Database pool timeout")
    database_pool_recycle: int = Field(default=3600, description="Database pool recycle time")
    
    # Redis settings
    redis_url: Optional[str] = Field(default=None, description="Redis connection URL")
    redis_db: int = Field(default=0, description="Redis database number")
    redis_password: Optional[str] = Field(default=None, description="Redis password")
    redis_socket_timeout: int = Field(default=5, description="Redis socket timeout")
    redis_socket_connect_timeout: int = Field(default=5, description="Redis connect timeout")
    redis_retry_on_timeout: bool = Field(default=True, description="Redis retry on timeout")
    
    # Cache settings
    cache_ttl: int = Field(default=3600, description="Default cache TTL in seconds")
    cache_prefix: str = Field(default="neo_core", description="Cache key prefix")
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["*"], description="Allowed CORS origins"
    )
    cors_credentials: bool = Field(default=True, description="Allow CORS credentials")
    cors_methods: List[str] = Field(
        default=["*"], description="Allowed CORS methods"
    )
    cors_headers: List[str] = Field(
        default=["*"], description="Allowed CORS headers"
    )
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format"
    )
    log_file: Optional[str] = Field(default=None, description="Log file path")
    log_rotation: str = Field(default="1 day", description="Log rotation interval")
    log_retention: str = Field(default="30 days", description="Log retention period")
    
    # Rate limiting settings
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per window")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # Pagination settings
    default_page_size: int = Field(default=20, description="Default pagination page size")
    max_page_size: int = Field(default=100, description="Maximum pagination page size")
    
    # File upload settings
    max_file_size: int = Field(default=10 * 1024 * 1024, description="Max file size in bytes")
    allowed_file_types: List[str] = Field(
        default=[".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx"],
        description="Allowed file extensions"
    )
    upload_path: str = Field(default="uploads", description="File upload directory")
    
    # Email settings
    smtp_host: Optional[str] = Field(default=None, description="SMTP host")
    smtp_port: int = Field(default=587, description="SMTP port")
    smtp_username: Optional[str] = Field(default=None, description="SMTP username")
    smtp_password: Optional[str] = Field(default=None, description="SMTP password")
    smtp_use_tls: bool = Field(default=True, description="Use TLS for SMTP")
    email_from: Optional[str] = Field(default=None, description="Default from email")
    
    # Celery settings
    celery_broker_url: Optional[str] = Field(default=None, description="Celery broker URL")
    celery_result_backend: Optional[str] = Field(default=None, description="Celery result backend")
    celery_task_serializer: str = Field(default="json", description="Celery task serializer")
    celery_result_serializer: str = Field(default="json", description="Celery result serializer")
    celery_timezone: str = Field(default="UTC", description="Celery timezone")
    
    # Monitoring settings
    enable_metrics: bool = Field(default=True, description="Enable metrics collection")
    metrics_path: str = Field(default="/metrics", description="Metrics endpoint path")
    health_check_path: str = Field(default="/health", description="Health check endpoint path")
    
    @validator("cors_origins", pre=True)
    def parse_cors_origins(cls, v: Any) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("cors_methods", pre=True)
    def parse_cors_methods(cls, v: Any) -> List[str]:
        """Parse CORS methods from string or list."""
        if isinstance(v, str):
            return [method.strip() for method in v.split(",")]
        return v
    
    @validator("cors_headers", pre=True)
    def parse_cors_headers(cls, v: Any) -> List[str]:
        """Parse CORS headers from string or list."""
        if isinstance(v, str):
            return [header.strip() for header in v.split(",")]
        return v
    
    @validator("allowed_file_types", pre=True)
    def parse_allowed_file_types(cls, v: Any) -> List[str]:
        """Parse allowed file types from string or list."""
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    @validator("log_level")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Invalid log level. Must be one of: {valid_levels}")
        return v.upper()
    
    @validator("environment")
    def validate_environment(cls, v: str) -> str:
        """Validate environment name."""
        valid_environments = ["development", "testing", "staging", "production"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Invalid environment. Must be one of: {valid_environments}")
        return v.lower()
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == "production"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == "testing"
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration dictionary."""
        return {
            "url": self.database_url,
            "echo": self.database_echo,
            "pool_size": self.database_pool_size,
            "max_overflow": self.database_max_overflow,
            "pool_timeout": self.database_pool_timeout,
            "pool_recycle": self.database_pool_recycle,
        }
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis configuration dictionary."""
        return {
            "url": self.redis_url,
            "db": self.redis_db,
            "password": self.redis_password,
            "socket_timeout": self.redis_socket_timeout,
            "socket_connect_timeout": self.redis_socket_connect_timeout,
            "retry_on_timeout": self.redis_retry_on_timeout,
        }
    
    def get_cors_config(self) -> Dict[str, Any]:
        """Get CORS configuration dictionary."""
        return {
            "allow_origins": self.cors_origins,
            "allow_credentials": self.cors_credentials,
            "allow_methods": self.cors_methods,
            "allow_headers": self.cors_headers,
        }
    
    def get_celery_config(self) -> Dict[str, Any]:
        """Get Celery configuration dictionary."""
        return {
            "broker_url": self.celery_broker_url or self.redis_url,
            "result_backend": self.celery_result_backend or self.redis_url,
            "task_serializer": self.celery_task_serializer,
            "result_serializer": self.celery_result_serializer,
            "timezone": self.celery_timezone,
        }


# Global settings instance
settings = CoreSettings()