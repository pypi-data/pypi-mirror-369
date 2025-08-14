"""Database session management and dependency injection."""

import logging
from typing import Generator, AsyncGenerator

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from .manager import DatabaseManager

logger = logging.getLogger(__name__)

# Global database manager instance
_db_manager: DatabaseManager = None


def get_database_manager() -> DatabaseManager:
    """Get or create database manager instance.
    
    Returns:
        DatabaseManager instance
    """
    global _db_manager
    
    if _db_manager is None:
        _db_manager = DatabaseManager(settings)
        _db_manager.initialize()
    
    return _db_manager


def get_db_session() -> Generator[Session, None, None]:
    """Dependency to get database session.
    
    This function is designed to be used with FastAPI's dependency injection system.
    
    Yields:
        Database session
    
    Example:
        ```python
        from fastapi import Depends
        from neo_core.database import get_db_session
        
        @app.get("/users/")
        def get_users(db: Session = Depends(get_db_session)):
            return db.query(User).all()
        ```
    """
    db_manager = get_database_manager()
    
    with db_manager.get_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            raise


async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get async database session.
    
    This function is designed to be used with FastAPI's dependency injection system
    for async endpoints.
    
    Yields:
        Async database session
    
    Example:
        ```python
        from fastapi import Depends
        from neo_core.database import get_async_db_session
        
        @app.get("/users/")
        async def get_users(db: AsyncSession = Depends(get_async_db_session)):
            result = await db.execute(select(User))
            return result.scalars().all()
        ```
    """
    db_manager = get_database_manager()
    
    async with db_manager.get_async_session() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Async database session error: {e}")
            raise


def create_session() -> Session:
    """Create a new database session.
    
    This function creates a new session that must be manually managed.
    Use get_db_session() for dependency injection instead.
    
    Returns:
        New database session
    
    Warning:
        Remember to close the session when done:
        ```python
        session = create_session()
        try:
            # Use session
            pass
        finally:
            session.close()
        ```
    """
    db_manager = get_database_manager()
    return db_manager._session_factory()


async def create_async_session() -> AsyncSession:
    """Create a new async database session.
    
    This function creates a new async session that must be manually managed.
    Use get_async_db_session() for dependency injection instead.
    
    Returns:
        New async database session
    
    Warning:
        Remember to close the session when done:
        ```python
        session = await create_async_session()
        try:
            # Use session
            pass
        finally:
            await session.close()
        ```
    """
    db_manager = get_database_manager()
    if not db_manager._async_session_factory:
        raise RuntimeError("Async session factory not available")
    return db_manager._async_session_factory()


def init_database() -> None:
    """Initialize database and create tables.
    
    This function should be called during application startup.
    """
    try:
        db_manager = get_database_manager()
        
        # Check connection
        if not db_manager.check_connection():
            raise RuntimeError("Failed to connect to database")
        
        # Create tables if they don't exist
        db_manager.create_all_tables()
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def init_async_database() -> None:
    """Initialize async database and check connection.
    
    This function should be called during application startup for async support.
    """
    try:
        db_manager = get_database_manager()
        
        # Check async connection if available
        if db_manager._async_engine:
            if not await db_manager.check_async_connection():
                logger.warning("Failed to connect to async database")
            else:
                logger.info("Async database connection verified")
        
    except Exception as e:
        logger.error(f"Failed to initialize async database: {e}")
        raise


def close_database() -> None:
    """Close database connections.
    
    This function should be called during application shutdown.
    """
    global _db_manager
    
    if _db_manager:
        try:
            _db_manager.close()
            logger.info("Database connections closed")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")
        finally:
            _db_manager = None


async def close_async_database() -> None:
    """Close async database connections.
    
    This function should be called during application shutdown for async support.
    """
    global _db_manager
    
    if _db_manager:
        try:
            await _db_manager.close_async()
            logger.info("Async database connections closed")
        except Exception as e:
            logger.error(f"Error closing async database connections: {e}")


def get_database_info() -> dict:
    """Get database connection information.
    
    Returns:
        Dictionary containing database information
    """
    try:
        db_manager = get_database_manager()
        return {
            "initialized": db_manager.is_initialized,
            "connection_healthy": db_manager.check_connection(),
            "engine_info": db_manager.get_engine_info(),
        }
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {
            "initialized": False,
            "connection_healthy": False,
            "error": str(e),
        }


# Dependency aliases for convenience
DbSession = Depends(get_db_session)
AsyncDbSession = Depends(get_async_db_session)