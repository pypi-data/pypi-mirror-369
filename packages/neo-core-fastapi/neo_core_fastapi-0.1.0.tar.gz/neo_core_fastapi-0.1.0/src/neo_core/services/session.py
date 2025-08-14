"""Session management services."""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from datetime import datetime, timedelta
import secrets
import hashlib

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from pydantic import BaseModel

from .base import BaseService, ServiceException, NotFoundError, ValidationException, DuplicateError
from .crud import UserSessionCRUDService
from ..models.session import UserSession, SessionActivity, RefreshToken
from ..models.session import SessionStatus, SessionType, DeviceType
from ..config import CoreSettings


class SessionCreateSchema(BaseModel):
    """Schema for creating a session."""
    user_id: UUID
    session_type: SessionType = SessionType.WEB
    device_type: DeviceType = DeviceType.DESKTOP
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    device_info: Optional[Dict[str, Any]] = None
    location_info: Optional[Dict[str, Any]] = None
    application_id: Optional[UUID] = None
    expires_in_seconds: Optional[int] = None
    remember_me: bool = False
    session_data: Optional[Dict[str, Any]] = None


class SessionUpdateSchema(BaseModel):
    """Schema for updating a session."""
    status: Optional[SessionStatus] = None
    device_info: Optional[Dict[str, Any]] = None
    location_info: Optional[Dict[str, Any]] = None
    session_data: Optional[Dict[str, Any]] = None
    termination_reason: Optional[str] = None


class SessionActivityCreateSchema(BaseModel):
    """Schema for creating session activity."""
    session_id: UUID
    activity_type: str
    description: Optional[str] = None
    request_path: Optional[str] = None
    request_method: Optional[str] = None
    response_status: Optional[int] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    additional_data: Optional[Dict[str, Any]] = None


class RefreshTokenCreateSchema(BaseModel):
    """Schema for creating a refresh token."""
    session_id: UUID
    expires_in_seconds: Optional[int] = None
    device_fingerprint: Optional[str] = None
    client_info: Optional[Dict[str, Any]] = None


class SessionService(BaseService):
    """Service for session management."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        self.session_crud = UserSessionCRUDService(settings)
        self.default_session_duration = 3600  # 1 hour
        self.default_remember_duration = 2592000  # 30 days
        self.max_sessions_per_user = 10
    
    def create_session(self, session_data: SessionCreateSchema) -> UserSession:
        """Create a new user session."""
        try:
            # Validate input
            session_data = self.validate_input(session_data, SessionCreateSchema)
            
            # Check if user has too many active sessions
            active_sessions = self.session_crud.get_active_sessions_by_user(session_data.user_id)
            if len(active_sessions) >= self.max_sessions_per_user:
                # Terminate oldest session
                oldest_session = min(active_sessions, key=lambda s: s.last_activity_at)
                self.terminate_session(oldest_session.id, "max_sessions_exceeded")
            
            # Generate session token
            session_token = self._generate_session_token()
            
            # Calculate expiration time
            if session_data.expires_in_seconds:
                expires_at = datetime.utcnow() + timedelta(seconds=session_data.expires_in_seconds)
            elif session_data.remember_me:
                expires_at = datetime.utcnow() + timedelta(seconds=self.default_remember_duration)
            else:
                expires_at = datetime.utcnow() + timedelta(seconds=self.default_session_duration)
            
            # Create session data
            create_data = {
                "id": uuid4(),
                "user_id": session_data.user_id,
                "session_token": session_token,
                "session_type": session_data.session_type,
                "status": SessionStatus.ACTIVE,
                "device_type": session_data.device_type,
                "client_ip": session_data.client_ip,
                "user_agent": session_data.user_agent,
                "device_info": session_data.device_info or {},
                "location_info": session_data.location_info or {},
                "application_id": session_data.application_id,
                "expires_at": expires_at,
                "last_activity_at": datetime.utcnow(),
                "session_data": session_data.session_data or {},
                "is_remember_me": session_data.remember_me,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create session
            session = self.session_crud.create(create_data)
            
            # Log session creation activity
            self.add_session_activity(
                session.id,
                "session_created",
                "User session created",
                client_ip=session_data.client_ip,
                user_agent=session_data.user_agent
            )
            
            self.log_operation("create_session", {
                "session_id": session.id,
                "user_id": session.user_id,
                "session_type": session.session_type,
                "device_type": session.device_type
            })
            
            return session
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create session")
    
    def get_session(self, session_id: UUID) -> Optional[UserSession]:
        """Get a session by ID."""
        return self.session_crud.get(session_id)
    
    def get_session_by_token(self, session_token: str) -> Optional[UserSession]:
        """Get a session by token."""
        return self.session_crud.get_by_token(session_token)
    
    def validate_session(self, session_token: str) -> Optional[UserSession]:
        """Validate a session token and return the session if valid."""
        try:
            session = self.get_session_by_token(session_token)
            if not session:
                return None
            
            # Check if session is active
            if session.status != SessionStatus.ACTIVE:
                return None
            
            # Check if session has expired
            if session.expires_at and session.expires_at < datetime.utcnow():
                self.terminate_session(session.id, "expired")
                return None
            
            # Update last activity
            self.update_session_activity(session.id)
            
            return session
        except Exception as e:
            self.handle_db_error(e, "validate session")
    
    def update_session(self, session_id: UUID, session_data: SessionUpdateSchema) -> UserSession:
        """Update a session."""
        try:
            # Validate input
            session_data = self.validate_input(session_data, SessionUpdateSchema)
            
            # Get existing session
            session = self.session_crud.get(session_id)
            if not session:
                raise NotFoundError("Session", session_id)
            
            # Update session data
            update_data = session_data.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.utcnow()
            
            # Update session
            updated_session = self.session_crud.update(session_id, update_data)
            
            self.log_operation("update_session", {
                "session_id": session_id,
                "updated_fields": list(update_data.keys())
            })
            
            return updated_session
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "update session")
    
    def extend_session(self, session_id: UUID, extend_seconds: int = None) -> UserSession:
        """Extend a session's expiration time."""
        try:
            session = self.session_crud.get(session_id)
            if not session:
                raise NotFoundError("Session", session_id)
            
            if session.status != SessionStatus.ACTIVE:
                raise ValidationException("Cannot extend inactive session")
            
            # Calculate new expiration time
            if extend_seconds is None:
                extend_seconds = self.default_session_duration
            
            new_expires_at = datetime.utcnow() + timedelta(seconds=extend_seconds)
            
            # Update session
            updated_session = self.session_crud.update(session_id, {
                "expires_at": new_expires_at,
                "updated_at": datetime.utcnow()
            })
            
            # Log activity
            self.add_session_activity(
                session_id,
                "session_extended",
                f"Session extended by {extend_seconds} seconds"
            )
            
            return updated_session
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "extend session")
    
    def update_session_activity(self, session_id: UUID, client_ip: str = None, user_agent: str = None) -> UserSession:
        """Update session's last activity time."""
        try:
            session = self.session_crud.get(session_id)
            if not session:
                raise NotFoundError("Session", session_id)
            
            update_data = {
                "last_activity_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Update client info if provided
            if client_ip:
                update_data["client_ip"] = client_ip
            if user_agent:
                update_data["user_agent"] = user_agent
            
            # Update session
            updated_session = self.session_crud.update(session_id, update_data)
            
            return updated_session
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "update session activity")
    
    def terminate_session(self, session_id: UUID, reason: str = "user_logout") -> bool:
        """Terminate a session."""
        try:
            session = self.session_crud.get(session_id)
            if not session:
                raise NotFoundError("Session", session_id)
            
            # Update session status
            self.session_crud.update(session_id, {
                "status": SessionStatus.TERMINATED,
                "terminated_at": datetime.utcnow(),
                "termination_reason": reason,
                "updated_at": datetime.utcnow()
            })
            
            # Log activity
            self.add_session_activity(
                session_id,
                "session_terminated",
                f"Session terminated: {reason}"
            )
            
            # Invalidate refresh tokens
            self._invalidate_refresh_tokens(session_id)
            
            self.log_operation("terminate_session", {
                "session_id": session_id,
                "reason": reason
            })
            
            return True
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "terminate session")
    
    def suspend_session(self, session_id: UUID, reason: str = "security_concern") -> UserSession:
        """Suspend a session."""
        try:
            session = self.session_crud.get(session_id)
            if not session:
                raise NotFoundError("Session", session_id)
            
            # Update session status
            updated_session = self.session_crud.update(session_id, {
                "status": SessionStatus.SUSPENDED,
                "suspension_reason": reason,
                "suspended_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            # Log activity
            self.add_session_activity(
                session_id,
                "session_suspended",
                f"Session suspended: {reason}"
            )
            
            return updated_session
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "suspend session")
    
    def reactivate_session(self, session_id: UUID) -> UserSession:
        """Reactivate a suspended session."""
        try:
            session = self.session_crud.get(session_id)
            if not session:
                raise NotFoundError("Session", session_id)
            
            if session.status != SessionStatus.SUSPENDED:
                raise ValidationException("Can only reactivate suspended sessions")
            
            # Check if session has expired
            if session.expires_at and session.expires_at < datetime.utcnow():
                raise ValidationException("Cannot reactivate expired session")
            
            # Update session status
            updated_session = self.session_crud.update(session_id, {
                "status": SessionStatus.ACTIVE,
                "suspension_reason": None,
                "suspended_at": None,
                "last_activity_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            
            # Log activity
            self.add_session_activity(
                session_id,
                "session_reactivated",
                "Session reactivated"
            )
            
            return updated_session
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "reactivate session")
    
    def terminate_user_sessions(self, user_id: UUID, exclude_session_id: UUID = None, reason: str = "user_action") -> int:
        """Terminate all sessions for a user."""
        try:
            # Get active sessions
            active_sessions = self.session_crud.get_active_sessions_by_user(user_id)
            
            terminated_count = 0
            for session in active_sessions:
                if exclude_session_id and session.id == exclude_session_id:
                    continue
                
                self.terminate_session(session.id, reason)
                terminated_count += 1
            
            self.log_operation("terminate_user_sessions", {
                "user_id": user_id,
                "terminated_count": terminated_count,
                "reason": reason
            })
            
            return terminated_count
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "terminate user sessions")
    
    def list_sessions(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        order_by: str = "last_activity_at",
        order_desc: bool = True
    ) -> List[UserSession]:
        """List sessions with filtering and pagination."""
        return self.session_crud.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=order_by,
            order_desc=order_desc
        )
    
    def get_user_sessions(self, user_id: UUID, active_only: bool = True) -> List[UserSession]:
        """Get sessions for a user."""
        if active_only:
            return self.session_crud.get_active_sessions_by_user(user_id)
        else:
            return self.session_crud.get_multi(filters={"user_id": user_id})
    
    def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions."""
        try:
            current_time = datetime.utcnow()
            
            # Get expired sessions
            expired_sessions = self.db.query(UserSession).filter(
                UserSession.expires_at < current_time,
                UserSession.status == SessionStatus.ACTIVE
            ).all()
            
            terminated_count = 0
            for session in expired_sessions:
                self.terminate_session(session.id, "expired")
                terminated_count += 1
            
            self.log_operation("cleanup_expired_sessions", {
                "terminated_count": terminated_count
            })
            
            return terminated_count
        except Exception as e:
            self.handle_db_error(e, "cleanup expired sessions")
    
    def add_session_activity(
        self,
        session_id: UUID,
        activity_type: str,
        description: str = None,
        request_path: str = None,
        request_method: str = None,
        response_status: int = None,
        client_ip: str = None,
        user_agent: str = None,
        additional_data: Dict[str, Any] = None
    ) -> SessionActivity:
        """Add activity to a session."""
        try:
            # Create activity data
            activity_data = {
                "id": uuid4(),
                "session_id": session_id,
                "activity_type": activity_type,
                "description": description,
                "request_path": request_path,
                "request_method": request_method,
                "response_status": response_status,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "additional_data": additional_data or {},
                "timestamp": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            
            # Create activity
            activity = SessionActivity(**activity_data)
            self.db.add(activity)
            self.db.commit()
            self.db.refresh(activity)
            
            return activity
        except Exception as e:
            self.db.rollback()
            self.handle_db_error(e, "add session activity")
    
    def get_session_activities(
        self,
        session_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[SessionActivity]:
        """Get activities for a session."""
        try:
            return (
                self.db.query(SessionActivity)
                .filter(SessionActivity.session_id == session_id)
                .order_by(SessionActivity.timestamp.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        except Exception as e:
            self.handle_db_error(e, "get session activities")
    
    def create_refresh_token(self, token_data: RefreshTokenCreateSchema) -> RefreshToken:
        """Create a refresh token for a session."""
        try:
            # Validate input
            token_data = self.validate_input(token_data, RefreshTokenCreateSchema)
            
            # Check if session exists
            session = self.session_crud.get(token_data.session_id)
            if not session:
                raise NotFoundError("Session", token_data.session_id)
            
            # Generate refresh token
            refresh_token = self._generate_refresh_token()
            
            # Calculate expiration time
            if token_data.expires_in_seconds:
                expires_at = datetime.utcnow() + timedelta(seconds=token_data.expires_in_seconds)
            else:
                expires_at = datetime.utcnow() + timedelta(seconds=self.default_remember_duration)
            
            # Create refresh token data
            create_data = {
                "id": uuid4(),
                "session_id": token_data.session_id,
                "refresh_token": refresh_token,
                "expires_at": expires_at,
                "device_fingerprint": token_data.device_fingerprint,
                "client_info": token_data.client_info or {},
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create refresh token
            token = RefreshToken(**create_data)
            self.db.add(token)
            self.db.commit()
            self.db.refresh(token)
            
            return token
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create refresh token")
    
    def validate_refresh_token(self, refresh_token: str) -> Optional[RefreshToken]:
        """Validate a refresh token."""
        try:
            token = (
                self.db.query(RefreshToken)
                .filter(
                    RefreshToken.refresh_token == refresh_token,
                    RefreshToken.is_active == True,
                    RefreshToken.expires_at > datetime.utcnow()
                )
                .first()
            )
            
            return token
        except Exception as e:
            self.handle_db_error(e, "validate refresh token")
    
    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Revoke a refresh token."""
        try:
            token = (
                self.db.query(RefreshToken)
                .filter(RefreshToken.refresh_token == refresh_token)
                .first()
            )
            
            if token:
                token.is_active = False
                token.revoked_at = datetime.utcnow()
                token.updated_at = datetime.utcnow()
                self.db.commit()
                return True
            
            return False
        except Exception as e:
            self.db.rollback()
            self.handle_db_error(e, "revoke refresh token")
    
    def _invalidate_refresh_tokens(self, session_id: UUID) -> None:
        """Invalidate all refresh tokens for a session."""
        try:
            self.db.query(RefreshToken).filter(
                RefreshToken.session_id == session_id
            ).update({
                "is_active": False,
                "revoked_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            })
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Failed to invalidate refresh tokens: {str(e)}")
    
    def _generate_session_token(self) -> str:
        """Generate a secure session token."""
        return secrets.token_urlsafe(32)
    
    def _generate_refresh_token(self) -> str:
        """Generate a secure refresh token."""
        return secrets.token_urlsafe(64)
    
    def get_session_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get session statistics."""
        try:
            # Default to last 30 days if no time range specified
            if not start_time:
                start_time = datetime.utcnow() - timedelta(days=30)
            if not end_time:
                end_time = datetime.utcnow()
            
            # Base query
            query = self.db.query(UserSession).filter(
                UserSession.created_at >= start_time,
                UserSession.created_at <= end_time
            )
            
            # Total sessions
            total_sessions = query.count()
            
            # Active sessions
            active_sessions = query.filter(UserSession.status == SessionStatus.ACTIVE).count()
            
            # Sessions by type
            type_counts = {}
            for session_type in SessionType:
                count = query.filter(UserSession.session_type == session_type).count()
                type_counts[session_type.value] = count
            
            # Sessions by device type
            device_counts = {}
            for device_type in DeviceType:
                count = query.filter(UserSession.device_type == device_type).count()
                device_counts[device_type.value] = count
            
            # Average session duration
            terminated_sessions = query.filter(
                UserSession.status == SessionStatus.TERMINATED,
                UserSession.terminated_at.isnot(None)
            ).all()
            
            total_duration = 0
            session_count = 0
            for session in terminated_sessions:
                if session.terminated_at and session.created_at:
                    duration = (session.terminated_at - session.created_at).total_seconds()
                    total_duration += duration
                    session_count += 1
            
            avg_duration = total_duration / session_count if session_count > 0 else 0
            
            return {
                "period": {
                    "start_time": start_time,
                    "end_time": end_time
                },
                "total_sessions": total_sessions,
                "active_sessions": active_sessions,
                "type_counts": type_counts,
                "device_counts": device_counts,
                "average_duration_seconds": avg_duration
            }
        except Exception as e:
            self.handle_db_error(e, "get session statistics")