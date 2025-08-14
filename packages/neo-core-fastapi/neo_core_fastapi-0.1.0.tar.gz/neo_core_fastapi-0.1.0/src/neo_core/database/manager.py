"""Database manager for handling connections and sessions."""

import logging
from contextlib import asynccontextmanager, contextmanager
from typing import AsyncGenerator, Generator, Optional, Dict, Any

from sqlalchemy import create_engine, event, pool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from alembic import command
from alembic.config import Config

from ..config import CoreSettings
from .base import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Database manager for handling connections and sessions."""
    
    def __init__(self, settings: CoreSettings):
        """Initialize database manager.
        
        Args:
            settings: Core application settings
        """
        self.settings = settings
        self._engine = None
        self._async_engine = None
        self._session_factory = None
        self._async_session_factory = None
        self._is_initialized = False
    
    def initialize(self) -> None:
        """Initialize database connections and session factories."""
        if self._is_initialized:
            logger.warning("Database manager already initialized")
            return
        
        try:
            # Create synchronous engine
            self._engine = self._create_engine()
            self._session_factory = sessionmaker(
                bind=self._engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False
            )
            
            # Create asynchronous engine
            async_url = self._get_async_database_url()
            if async_url:
                self._async_engine = self._create_async_engine(async_url)
                self._async_session_factory = async_sessionmaker(
                    bind=self._async_engine,
                    class_=AsyncSession,
                    autocommit=False,
                    autoflush=False,
                    expire_on_commit=False
                )
            
            # Set up event listeners
            self._setup_event_listeners()
            
            self._is_initialized = True
            logger.info("Database manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize database manager: {e}")
            raise
    
    def _create_engine(self):
        """Create synchronous database engine."""
        config = self.settings.get_database_config()
        
        engine_kwargs = {
            "echo": config["echo"],
            "poolclass": QueuePool,
            "pool_size": config["pool_size"],
            "max_overflow": config["max_overflow"],
            "pool_timeout": config["pool_timeout"],
            "pool_recycle": config["pool_recycle"],
            "pool_pre_ping": True,
        }
        
        return create_engine(config["url"], **engine_kwargs)
    
    def _create_async_engine(self, url: str):
        """Create asynchronous database engine."""
        config = self.settings.get_database_config()
        
        engine_kwargs = {
            "echo": config["echo"],
            "pool_size": config["pool_size"],
            "max_overflow": config["max_overflow"],
            "pool_timeout": config["pool_timeout"],
            "pool_recycle": config["pool_recycle"],
            "pool_pre_ping": True,
        }
        
        return create_async_engine(url, **engine_kwargs)
    
    def _get_async_database_url(self) -> Optional[str]:
        """Convert sync database URL to async URL."""
        url = self.settings.database_url
        
        # Convert common sync drivers to async
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://")
        elif url.startswith("mysql://"):
            return url.replace("mysql://", "mysql+aiomysql://")
        elif url.startswith("sqlite://"):
            return url.replace("sqlite://", "sqlite+aiosqlite://")
        
        return None
    
    def _setup_event_listeners(self) -> None:
        """Set up database event listeners."""
        if self._engine:
            # Log slow queries
            @event.listens_for(self._engine, "before_cursor_execute")
            def receive_before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                context._query_start_time = logger.time()
            
            @event.listens_for(self._engine, "after_cursor_execute")
            def receive_after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
                total = logger.time() - context._query_start_time
                if total > 1.0:  # Log queries taking more than 1 second
                    logger.warning(f"Slow query detected: {total:.2f}s - {statement[:100]}...")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Get database session context manager.
        
        Yields:
            Database session
        """
        if not self._is_initialized:
            raise RuntimeError("Database manager not initialized")
        
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    @asynccontextmanager
    async def get_async_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session context manager.
        
        Yields:
            Async database session
        """
        if not self._is_initialized or not self._async_session_factory:
            raise RuntimeError("Async database manager not initialized")
        
        session = self._async_session_factory()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    def create_all_tables(self) -> None:
        """Create all database tables."""
        if not self._is_initialized:
            raise RuntimeError("Database manager not initialized")
        
        try:
            Base.metadata.create_all(bind=self._engine)
            logger.info("All database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def drop_all_tables(self) -> None:
        """Drop all database tables."""
        if not self._is_initialized:
            raise RuntimeError("Database manager not initialized")
        
        try:
            Base.metadata.drop_all(bind=self._engine)
            logger.info("All database tables dropped successfully")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise
    
    def run_migrations(self, alembic_cfg_path: str = "alembic.ini") -> None:
        """Run database migrations.
        
        Args:
            alembic_cfg_path: Path to alembic configuration file
        """
        try:
            alembic_cfg = Config(alembic_cfg_path)
            alembic_cfg.set_main_option("sqlalchemy.url", self.settings.database_url)
            command.upgrade(alembic_cfg, "head")
            logger.info("Database migrations completed successfully")
        except Exception as e:
            logger.error(f"Failed to run database migrations: {e}")
            raise
    
    def check_connection(self) -> bool:
        """Check database connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection check failed: {e}")
            return False
    
    async def check_async_connection(self) -> bool:
        """Check async database connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            async with self.get_async_session() as session:
                await session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Async database connection check failed: {e}")
            return False
    
    def get_engine_info(self) -> Dict[str, Any]:
        """Get database engine information.
        
        Returns:
            Dictionary containing engine information
        """
        if not self._engine:
            return {}
        
        pool = self._engine.pool
        return {
            "url": str(self._engine.url).replace(self._engine.url.password or "", "***"),
            "driver": self._engine.driver,
            "pool_size": pool.size() if hasattr(pool, 'size') else None,
            "checked_in": pool.checkedin() if hasattr(pool, 'checkedin') else None,
            "checked_out": pool.checkedout() if hasattr(pool, 'checkedout') else None,
            "overflow": pool.overflow() if hasattr(pool, 'overflow') else None,
        }
    
    def close(self) -> None:
        """Close database connections."""
        try:
            if self._engine:
                self._engine.dispose()
                logger.info("Synchronous database engine disposed")
            
            if self._async_engine:
                # Note: async engine disposal should be awaited in async context
                logger.info("Async database engine marked for disposal")
            
            self._is_initialized = False
            
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
    
    async def close_async(self) -> None:
        """Close async database connections."""
        try:
            if self._async_engine:
                await self._async_engine.dispose()
                logger.info("Async database engine disposed")
        except Exception as e:
            logger.error(f"Error closing async database connections: {e}")
    
    @property
    def engine(self):
        """Get synchronous database engine."""
        return self._engine
    
    @property
    def async_engine(self):
        """Get asynchronous database engine."""
        return self._async_engine
    
    @property
    def is_initialized(self) -> bool:
        """Check if database manager is initialized."""
        return self._is_initialized