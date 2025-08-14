"""Cache management services."""

from typing import Any, Optional, Dict, List, Union
from datetime import datetime, timedelta
import json
import pickle
import hashlib
from abc import ABC, abstractmethod

try:
    import redis
    from redis import Redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    Redis = None

from .base import BaseService, ServiceException
from ..config import CoreSettings


class CacheException(ServiceException):
    """Cache-related exception."""
    pass


class CacheKeyError(CacheException):
    """Cache key error."""
    pass


class CacheConnectionError(CacheException):
    """Cache connection error."""
    pass


class BaseCacheService(ABC):
    """Abstract base class for cache services."""
    
    @abstractmethod
    def get(self, key: str) -> Any:
        """Get value from cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Clear all cache."""
        pass
    
    @abstractmethod
    def get_ttl(self, key: str) -> Optional[int]:
        """Get TTL for key."""
        pass
    
    @abstractmethod
    def set_ttl(self, key: str, ttl: int) -> bool:
        """Set TTL for key."""
        pass


class MemoryCacheService(BaseCacheService):
    """In-memory cache service (for development/testing)."""
    
    def __init__(self):
        self._cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Any:
        """Get value from memory cache."""
        if key not in self._cache:
            return None
        
        item = self._cache[key]
        
        # Check if expired
        if item.get('expires_at') and datetime.utcnow() > item['expires_at']:
            del self._cache[key]
            return None
        
        return item['value']
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in memory cache."""
        expires_at = None
        if ttl:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl)
        
        self._cache[key] = {
            'value': value,
            'expires_at': expires_at,
            'created_at': datetime.utcnow()
        }
        
        return True
    
    def delete(self, key: str) -> bool:
        """Delete key from memory cache."""
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in memory cache."""
        if key not in self._cache:
            return False
        
        item = self._cache[key]
        
        # Check if expired
        if item.get('expires_at') and datetime.utcnow() > item['expires_at']:
            del self._cache[key]
            return False
        
        return True
    
    def clear(self) -> bool:
        """Clear all memory cache."""
        self._cache.clear()
        return True
    
    def get_ttl(self, key: str) -> Optional[int]:
        """Get TTL for key in memory cache."""
        if key not in self._cache:
            return None
        
        item = self._cache[key]
        if not item.get('expires_at'):
            return -1  # No expiration
        
        remaining = item['expires_at'] - datetime.utcnow()
        return max(0, int(remaining.total_seconds()))
    
    def set_ttl(self, key: str, ttl: int) -> bool:
        """Set TTL for key in memory cache."""
        if key not in self._cache:
            return False
        
        self._cache[key]['expires_at'] = datetime.utcnow() + timedelta(seconds=ttl)
        return True


class RedisCacheService(BaseCacheService):
    """Redis cache service."""
    
    def __init__(self, settings: CoreSettings = None):
        if not REDIS_AVAILABLE:
            raise CacheException("Redis is not available. Please install redis package.")
        
        self.settings = settings or CoreSettings()
        
        # Redis connection parameters
        self.host = getattr(self.settings, 'REDIS_HOST', 'localhost')
        self.port = getattr(self.settings, 'REDIS_PORT', 6379)
        self.db = getattr(self.settings, 'REDIS_DB', 0)
        self.password = getattr(self.settings, 'REDIS_PASSWORD', None)
        self.decode_responses = getattr(self.settings, 'REDIS_DECODE_RESPONSES', True)
        
        # Connection pool settings
        self.max_connections = getattr(self.settings, 'REDIS_MAX_CONNECTIONS', 10)
        self.socket_timeout = getattr(self.settings, 'REDIS_SOCKET_TIMEOUT', 5)
        self.socket_connect_timeout = getattr(self.settings, 'REDIS_SOCKET_CONNECT_TIMEOUT', 5)
        
        # Key prefix
        self.key_prefix = getattr(self.settings, 'REDIS_KEY_PREFIX', 'neo_core:')
        
        # Serialization method
        self.serialization = getattr(self.settings, 'REDIS_SERIALIZATION', 'json')  # json or pickle
        
        self._redis: Optional[Redis] = None
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Redis."""
        try:
            self._redis = Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=self.decode_responses,
                max_connections=self.max_connections,
                socket_timeout=self.socket_timeout,
                socket_connect_timeout=self.socket_connect_timeout
            )
            
            # Test connection
            self._redis.ping()
        except Exception as e:
            raise CacheConnectionError(f"Failed to connect to Redis: {str(e)}")
    
    def _get_key(self, key: str) -> str:
        """Get prefixed key."""
        return f"{self.key_prefix}{key}"
    
    def _serialize(self, value: Any) -> Union[str, bytes]:
        """Serialize value for storage."""
        if self.serialization == 'pickle':
            return pickle.dumps(value)
        else:
            # JSON serialization
            if isinstance(value, (str, int, float, bool)):
                return value
            return json.dumps(value, default=str)
    
    def _deserialize(self, value: Union[str, bytes]) -> Any:
        """Deserialize value from storage."""
        if value is None:
            return None
        
        if self.serialization == 'pickle':
            return pickle.loads(value)
        else:
            # JSON deserialization
            if isinstance(value, (int, float, bool)):
                return value
            if isinstance(value, str):
                try:
                    return json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    return value
            return value
    
    def get(self, key: str) -> Any:
        """Get value from Redis cache."""
        try:
            value = self._redis.get(self._get_key(key))
            return self._deserialize(value)
        except Exception as e:
            raise CacheException(f"Failed to get key '{key}': {str(e)}")
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis cache."""
        try:
            serialized_value = self._serialize(value)
            result = self._redis.set(self._get_key(key), serialized_value, ex=ttl)
            return bool(result)
        except Exception as e:
            raise CacheException(f"Failed to set key '{key}': {str(e)}")
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis cache."""
        try:
            result = self._redis.delete(self._get_key(key))
            return bool(result)
        except Exception as e:
            raise CacheException(f"Failed to delete key '{key}': {str(e)}")
    
    def exists(self, key: str) -> bool:
        """Check if key exists in Redis cache."""
        try:
            result = self._redis.exists(self._get_key(key))
            return bool(result)
        except Exception as e:
            raise CacheException(f"Failed to check key '{key}': {str(e)}")
    
    def clear(self) -> bool:
        """Clear all cache with prefix."""
        try:
            # Get all keys with prefix
            pattern = f"{self.key_prefix}*"
            keys = self._redis.keys(pattern)
            
            if keys:
                result = self._redis.delete(*keys)
                return bool(result)
            
            return True
        except Exception as e:
            raise CacheException(f"Failed to clear cache: {str(e)}")
    
    def get_ttl(self, key: str) -> Optional[int]:
        """Get TTL for key in Redis cache."""
        try:
            ttl = self._redis.ttl(self._get_key(key))
            if ttl == -2:  # Key doesn't exist
                return None
            if ttl == -1:  # Key exists but no expiration
                return -1
            return ttl
        except Exception as e:
            raise CacheException(f"Failed to get TTL for key '{key}': {str(e)}")
    
    def set_ttl(self, key: str, ttl: int) -> bool:
        """Set TTL for key in Redis cache."""
        try:
            result = self._redis.expire(self._get_key(key), ttl)
            return bool(result)
        except Exception as e:
            raise CacheException(f"Failed to set TTL for key '{key}': {str(e)}")
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment numeric value in Redis cache."""
        try:
            result = self._redis.incrby(self._get_key(key), amount)
            return int(result)
        except Exception as e:
            raise CacheException(f"Failed to increment key '{key}': {str(e)}")
    
    def decrement(self, key: str, amount: int = 1) -> int:
        """Decrement numeric value in Redis cache."""
        try:
            result = self._redis.decrby(self._get_key(key), amount)
            return int(result)
        except Exception as e:
            raise CacheException(f"Failed to decrement key '{key}': {str(e)}")
    
    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from Redis cache."""
        try:
            prefixed_keys = [self._get_key(key) for key in keys]
            values = self._redis.mget(prefixed_keys)
            
            result = {}
            for i, key in enumerate(keys):
                result[key] = self._deserialize(values[i])
            
            return result
        except Exception as e:
            raise CacheException(f"Failed to get multiple keys: {str(e)}")
    
    def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in Redis cache."""
        try:
            # Prepare data
            prefixed_mapping = {}
            for key, value in mapping.items():
                prefixed_mapping[self._get_key(key)] = self._serialize(value)
            
            # Set values
            result = self._redis.mset(prefixed_mapping)
            
            # Set TTL if specified
            if ttl and result:
                for key in mapping.keys():
                    self._redis.expire(self._get_key(key), ttl)
            
            return bool(result)
        except Exception as e:
            raise CacheException(f"Failed to set multiple keys: {str(e)}")
    
    def delete_many(self, keys: List[str]) -> int:
        """Delete multiple keys from Redis cache."""
        try:
            prefixed_keys = [self._get_key(key) for key in keys]
            result = self._redis.delete(*prefixed_keys)
            return int(result)
        except Exception as e:
            raise CacheException(f"Failed to delete multiple keys: {str(e)}")
    
    def get_keys(self, pattern: str = "*") -> List[str]:
        """Get keys matching pattern."""
        try:
            full_pattern = f"{self.key_prefix}{pattern}"
            keys = self._redis.keys(full_pattern)
            
            # Remove prefix from keys
            prefix_len = len(self.key_prefix)
            return [key[prefix_len:] for key in keys]
        except Exception as e:
            raise CacheException(f"Failed to get keys with pattern '{pattern}': {str(e)}")
    
    def flush_db(self) -> bool:
        """Flush entire Redis database."""
        try:
            result = self._redis.flushdb()
            return bool(result)
        except Exception as e:
            raise CacheException(f"Failed to flush database: {str(e)}")
    
    def get_info(self) -> Dict[str, Any]:
        """Get Redis server info."""
        try:
            return self._redis.info()
        except Exception as e:
            raise CacheException(f"Failed to get Redis info: {str(e)}")
    
    def ping(self) -> bool:
        """Ping Redis server."""
        try:
            result = self._redis.ping()
            return bool(result)
        except Exception as e:
            return False


class CacheService(BaseService):
    """Main cache service with multiple backends."""
    
    def __init__(self, settings: CoreSettings = None, backend: str = "auto"):
        super().__init__(settings)
        
        self.backend_type = backend
        self.default_ttl = getattr(self.settings, 'CACHE_DEFAULT_TTL', 3600)  # 1 hour
        
        # Initialize cache backend
        if backend == "auto":
            # Try Redis first, fallback to memory
            try:
                if REDIS_AVAILABLE:
                    self.backend = RedisCacheService(settings)
                    self.backend_type = "redis"
                else:
                    self.backend = MemoryCacheService()
                    self.backend_type = "memory"
            except CacheConnectionError:
                self.backend = MemoryCacheService()
                self.backend_type = "memory"
        elif backend == "redis":
            self.backend = RedisCacheService(settings)
            self.backend_type = "redis"
        elif backend == "memory":
            self.backend = MemoryCacheService()
            self.backend_type = "memory"
        else:
            raise CacheException(f"Unknown cache backend: {backend}")
        
        self.logger.info(f"Cache service initialized with {self.backend_type} backend")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        try:
            value = self.backend.get(key)
            return value if value is not None else default
        except Exception as e:
            self.logger.error(f"Cache get error for key '{key}': {str(e)}")
            return default
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        try:
            if ttl is None:
                ttl = self.default_ttl
            
            return self.backend.set(key, value, ttl)
        except Exception as e:
            self.logger.error(f"Cache set error for key '{key}': {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        try:
            return self.backend.delete(key)
        except Exception as e:
            self.logger.error(f"Cache delete error for key '{key}': {str(e)}")
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        try:
            return self.backend.exists(key)
        except Exception as e:
            self.logger.error(f"Cache exists error for key '{key}': {str(e)}")
            return False
    
    def clear(self) -> bool:
        """Clear all cache."""
        try:
            return self.backend.clear()
        except Exception as e:
            self.logger.error(f"Cache clear error: {str(e)}")
            return False
    
    def get_ttl(self, key: str) -> Optional[int]:
        """Get TTL for key."""
        try:
            return self.backend.get_ttl(key)
        except Exception as e:
            self.logger.error(f"Cache get_ttl error for key '{key}': {str(e)}")
            return None
    
    def set_ttl(self, key: str, ttl: int) -> bool:
        """Set TTL for key."""
        try:
            return self.backend.set_ttl(key, ttl)
        except Exception as e:
            self.logger.error(f"Cache set_ttl error for key '{key}': {str(e)}")
            return False
    
    def get_or_set(self, key: str, func, ttl: Optional[int] = None, *args, **kwargs) -> Any:
        """Get value from cache or set it using function."""
        value = self.get(key)
        if value is not None:
            return value
        
        # Generate value using function
        try:
            value = func(*args, **kwargs)
            self.set(key, value, ttl)
            return value
        except Exception as e:
            self.logger.error(f"Cache get_or_set error for key '{key}': {str(e)}")
            raise
    
    def cache_result(self, ttl: Optional[int] = None, key_func=None):
        """Decorator to cache function results."""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Generate cache key
                if key_func:
                    cache_key = key_func(*args, **kwargs)
                else:
                    cache_key = self._generate_cache_key(func.__name__, args, kwargs)
                
                # Try to get from cache
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Execute function and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result
            
            return wrapper
        return decorator
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate keys matching pattern (Redis only)."""
        if self.backend_type != "redis":
            self.logger.warning("Pattern invalidation only supported with Redis backend")
            return 0
        
        try:
            keys = self.backend.get_keys(pattern)
            if keys:
                return self.backend.delete_many(keys)
            return 0
        except Exception as e:
            self.logger.error(f"Cache invalidate_pattern error for pattern '{pattern}': {str(e)}")
            return 0
    
    def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """Get multiple values from cache."""
        if self.backend_type == "redis":
            try:
                return self.backend.get_many(keys)
            except Exception as e:
                self.logger.error(f"Cache get_many error: {str(e)}")
                return {}
        else:
            # Fallback for memory cache
            result = {}
            for key in keys:
                result[key] = self.get(key)
            return result
    
    def set_many(self, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """Set multiple values in cache."""
        if self.backend_type == "redis":
            try:
                return self.backend.set_many(mapping, ttl)
            except Exception as e:
                self.logger.error(f"Cache set_many error: {str(e)}")
                return False
        else:
            # Fallback for memory cache
            success = True
            for key, value in mapping.items():
                if not self.set(key, value, ttl):
                    success = False
            return success
    
    def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment numeric value in cache."""
        if self.backend_type == "redis":
            try:
                return self.backend.increment(key, amount)
            except Exception as e:
                self.logger.error(f"Cache increment error for key '{key}': {str(e)}")
                return None
        else:
            # Fallback for memory cache
            try:
                current = self.get(key, 0)
                new_value = int(current) + amount
                self.set(key, new_value)
                return new_value
            except Exception as e:
                self.logger.error(f"Cache increment error for key '{key}': {str(e)}")
                return None
    
    def decrement(self, key: str, amount: int = 1) -> Optional[int]:
        """Decrement numeric value in cache."""
        return self.increment(key, -amount)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            "backend": self.backend_type,
            "default_ttl": self.default_ttl
        }
        
        if self.backend_type == "redis":
            try:
                redis_info = self.backend.get_info()
                stats.update({
                    "redis_version": redis_info.get("redis_version"),
                    "used_memory": redis_info.get("used_memory_human"),
                    "connected_clients": redis_info.get("connected_clients"),
                    "total_commands_processed": redis_info.get("total_commands_processed")
                })
            except Exception as e:
                self.logger.error(f"Failed to get Redis stats: {str(e)}")
        
        return stats
    
    def health_check(self) -> Dict[str, Any]:
        """Check cache health."""
        try:
            # Test basic operations
            test_key = "__health_check__"
            test_value = "ok"
            
            # Test set
            set_success = self.set(test_key, test_value, 60)
            
            # Test get
            get_value = self.get(test_key)
            get_success = get_value == test_value
            
            # Test delete
            delete_success = self.delete(test_key)
            
            # Additional checks for Redis
            ping_success = True
            if self.backend_type == "redis":
                ping_success = self.backend.ping()
            
            is_healthy = all([set_success, get_success, delete_success, ping_success])
            
            return {
                "healthy": is_healthy,
                "backend": self.backend_type,
                "checks": {
                    "set": set_success,
                    "get": get_success,
                    "delete": delete_success,
                    "ping": ping_success
                }
            }
        except Exception as e:
            return {
                "healthy": False,
                "backend": self.backend_type,
                "error": str(e)
            }
    
    def _generate_cache_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key for function call."""
        # Create a hash of the function name and arguments
        key_data = {
            "func": func_name,
            "args": args,
            "kwargs": sorted(kwargs.items())
        }
        
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        
        return f"func_cache:{func_name}:{key_hash}"