"""Audit logging services."""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from datetime import datetime, timedelta

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func, desc
from pydantic import BaseModel

from .base import BaseService, ServiceException, NotFoundError, ValidationException
from .crud import AuditLogCRUDService
from ..models.audit import AuditLog, AuditTrail, AuditTrailEntry
from ..models.audit import AuditAction, AuditLevel, AuditStatus
from ..config import CoreSettings


class AuditLogCreateSchema(BaseModel):
    """Schema for creating an audit log entry."""
    user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    action: AuditAction
    resource_type: str
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    request_method: Optional[str] = None
    request_path: Optional[str] = None
    request_query: Optional[Dict[str, Any]] = None
    request_body: Optional[Dict[str, Any]] = None
    response_status: Optional[int] = None
    response_body: Optional[Dict[str, Any]] = None
    client_ip: Optional[str] = None
    user_agent: Optional[str] = None
    application_id: Optional[UUID] = None
    module_id: Optional[UUID] = None
    level: AuditLevel = AuditLevel.INFO
    status: AuditStatus = AuditStatus.SUCCESS
    message: Optional[str] = None
    description: Optional[str] = None
    old_values: Optional[Dict[str, Any]] = None
    new_values: Optional[Dict[str, Any]] = None
    changed_fields: Optional[List[str]] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = None
    execution_time_ms: Optional[int] = None
    memory_usage_mb: Optional[float] = None
    additional_data: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None


class AuditLogFilterSchema(BaseModel):
    """Schema for filtering audit logs."""
    user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    action: Optional[AuditAction] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    application_id: Optional[UUID] = None
    module_id: Optional[UUID] = None
    level: Optional[AuditLevel] = None
    status: Optional[AuditStatus] = None
    client_ip: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    tags: Optional[List[str]] = None
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None


class AuditTrailCreateSchema(BaseModel):
    """Schema for creating an audit trail."""
    name: str
    description: Optional[str] = None
    user_id: Optional[UUID] = None
    session_id: Optional[UUID] = None
    application_id: Optional[UUID] = None
    correlation_id: Optional[str] = None
    trace_id: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class AuditService(BaseService):
    """Service for audit logging and management."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        self.audit_crud = AuditLogCRUDService(settings)
    
    def log_action(
        self,
        action: AuditAction,
        resource_type: str,
        user_id: Optional[UUID] = None,
        session_id: Optional[UUID] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        level: AuditLevel = AuditLevel.INFO,
        status: AuditStatus = AuditStatus.SUCCESS,
        message: Optional[str] = None,
        description: Optional[str] = None,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        changed_fields: Optional[List[str]] = None,
        request_data: Optional[Dict[str, Any]] = None,
        response_data: Optional[Dict[str, Any]] = None,
        client_info: Optional[Dict[str, str]] = None,
        application_id: Optional[UUID] = None,
        module_id: Optional[UUID] = None,
        error_info: Optional[Dict[str, Any]] = None,
        performance_info: Optional[Dict[str, Any]] = None,
        additional_data: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        correlation_id: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None
    ) -> AuditLog:
        """Log an audit action."""
        try:
            # Prepare audit log data
            audit_data = {
                "id": uuid4(),
                "user_id": user_id,
                "session_id": session_id,
                "action": action,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "resource_name": resource_name,
                "level": level,
                "status": status,
                "message": message,
                "description": description,
                "old_values": old_values or {},
                "new_values": new_values or {},
                "changed_fields": changed_fields or [],
                "application_id": application_id,
                "module_id": module_id,
                "additional_data": additional_data or {},
                "tags": tags or [],
                "correlation_id": correlation_id,
                "trace_id": trace_id,
                "span_id": span_id,
                "timestamp": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            
            # Add request data
            if request_data:
                audit_data.update({
                    "request_method": request_data.get("method"),
                    "request_path": request_data.get("path"),
                    "request_query": request_data.get("query"),
                    "request_body": request_data.get("body")
                })
            
            # Add response data
            if response_data:
                audit_data.update({
                    "response_status": response_data.get("status"),
                    "response_body": response_data.get("body")
                })
            
            # Add client info
            if client_info:
                audit_data.update({
                    "client_ip": client_info.get("ip"),
                    "user_agent": client_info.get("user_agent")
                })
            
            # Add error info
            if error_info:
                audit_data.update({
                    "error_code": error_info.get("code"),
                    "error_message": error_info.get("message"),
                    "error_details": error_info.get("details")
                })
            
            # Add performance info
            if performance_info:
                audit_data.update({
                    "execution_time_ms": performance_info.get("execution_time_ms"),
                    "memory_usage_mb": performance_info.get("memory_usage_mb")
                })
            
            # Create audit log
            audit_log = self.audit_crud.create(audit_data)
            
            return audit_log
        except Exception as e:
            # Don't raise exceptions for audit logging to avoid breaking main operations
            self.logger.error(f"Failed to create audit log: {str(e)}")
            return None
    
    def create_audit_log(self, audit_data: AuditLogCreateSchema) -> AuditLog:
        """Create a new audit log entry."""
        try:
            # Validate input
            audit_data = self.validate_input(audit_data, AuditLogCreateSchema)
            
            # Create audit log data
            create_data = {
                "id": uuid4(),
                "user_id": audit_data.user_id,
                "session_id": audit_data.session_id,
                "action": audit_data.action,
                "resource_type": audit_data.resource_type,
                "resource_id": audit_data.resource_id,
                "resource_name": audit_data.resource_name,
                "request_method": audit_data.request_method,
                "request_path": audit_data.request_path,
                "request_query": audit_data.request_query or {},
                "request_body": audit_data.request_body or {},
                "response_status": audit_data.response_status,
                "response_body": audit_data.response_body or {},
                "client_ip": audit_data.client_ip,
                "user_agent": audit_data.user_agent,
                "application_id": audit_data.application_id,
                "module_id": audit_data.module_id,
                "level": audit_data.level,
                "status": audit_data.status,
                "message": audit_data.message,
                "description": audit_data.description,
                "old_values": audit_data.old_values or {},
                "new_values": audit_data.new_values or {},
                "changed_fields": audit_data.changed_fields or [],
                "error_code": audit_data.error_code,
                "error_message": audit_data.error_message,
                "error_details": audit_data.error_details or {},
                "execution_time_ms": audit_data.execution_time_ms,
                "memory_usage_mb": audit_data.memory_usage_mb,
                "additional_data": audit_data.additional_data or {},
                "tags": audit_data.tags or [],
                "correlation_id": audit_data.correlation_id,
                "trace_id": audit_data.trace_id,
                "span_id": audit_data.span_id,
                "timestamp": datetime.utcnow(),
                "created_at": datetime.utcnow()
            }
            
            # Create audit log
            audit_log = self.audit_crud.create(create_data)
            
            return audit_log
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create audit log")
    
    def get_audit_log(self, audit_id: UUID) -> Optional[AuditLog]:
        """Get an audit log by ID."""
        return self.audit_crud.get(audit_id)
    
    def list_audit_logs(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[AuditLogFilterSchema] = None,
        order_by: str = "timestamp",
        order_desc: bool = True
    ) -> List[AuditLog]:
        """List audit logs with filtering and pagination."""
        try:
            # Convert filter schema to dict
            filter_dict = {}
            if filters:
                filter_data = filters.dict(exclude_unset=True)
                
                # Handle date range filters
                if "start_time" in filter_data or "end_time" in filter_data:
                    date_filters = []
                    if "start_time" in filter_data:
                        date_filters.append(AuditLog.timestamp >= filter_data.pop("start_time"))
                    if "end_time" in filter_data:
                        date_filters.append(AuditLog.timestamp <= filter_data.pop("end_time"))
                    filter_dict["_date_range"] = date_filters
                
                # Handle tag filters
                if "tags" in filter_data:
                    tags = filter_data.pop("tags")
                    if tags:
                        filter_dict["_tags"] = tags
                
                # Add remaining filters
                filter_dict.update(filter_data)
            
            return self.audit_crud.get_multi(
                skip=skip,
                limit=limit,
                filters=filter_dict,
                order_by=order_by,
                order_desc=order_desc
            )
        except Exception as e:
            self.handle_db_error(e, "list audit logs")
    
    def get_audit_logs_by_user(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AuditLog]:
        """Get audit logs by user."""
        filters = {"user_id": user_id}
        
        if start_time or end_time:
            date_filters = []
            if start_time:
                date_filters.append(AuditLog.timestamp >= start_time)
            if end_time:
                date_filters.append(AuditLog.timestamp <= end_time)
            filters["_date_range"] = date_filters
        
        return self.audit_crud.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="timestamp",
            order_desc=True
        )
    
    def get_audit_logs_by_resource(
        self,
        resource_type: str,
        resource_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AuditLog]:
        """Get audit logs by resource."""
        filters = {"resource_type": resource_type}
        
        if resource_id:
            filters["resource_id"] = resource_id
        
        if start_time or end_time:
            date_filters = []
            if start_time:
                date_filters.append(AuditLog.timestamp >= start_time)
            if end_time:
                date_filters.append(AuditLog.timestamp <= end_time)
            filters["_date_range"] = date_filters
        
        return self.audit_crud.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="timestamp",
            order_desc=True
        )
    
    def get_audit_logs_by_session(
        self,
        session_id: UUID,
        skip: int = 0,
        limit: int = 100
    ) -> List[AuditLog]:
        """Get audit logs by session."""
        return self.audit_crud.get_multi(
            skip=skip,
            limit=limit,
            filters={"session_id": session_id},
            order_by="timestamp",
            order_desc=True
        )
    
    def get_audit_logs_by_application(
        self,
        application_id: UUID,
        skip: int = 0,
        limit: int = 100,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[AuditLog]:
        """Get audit logs by application."""
        filters = {"application_id": application_id}
        
        if start_time or end_time:
            date_filters = []
            if start_time:
                date_filters.append(AuditLog.timestamp >= start_time)
            if end_time:
                date_filters.append(AuditLog.timestamp <= end_time)
            filters["_date_range"] = date_filters
        
        return self.audit_crud.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by="timestamp",
            order_desc=True
        )
    
    def get_audit_statistics(
        self,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        group_by: str = "action"
    ) -> Dict[str, Any]:
        """Get audit statistics."""
        try:
            # Default to last 30 days if no time range specified
            if not start_time:
                start_time = datetime.utcnow() - timedelta(days=30)
            if not end_time:
                end_time = datetime.utcnow()
            
            # Base query
            query = self.db.query(AuditLog).filter(
                AuditLog.timestamp >= start_time,
                AuditLog.timestamp <= end_time
            )
            
            # Total count
            total_count = query.count()
            
            # Count by status
            status_counts = {}
            for status in AuditStatus:
                count = query.filter(AuditLog.status == status).count()
                status_counts[status.value] = count
            
            # Count by level
            level_counts = {}
            for level in AuditLevel:
                count = query.filter(AuditLog.level == level).count()
                level_counts[level.value] = count
            
            # Count by action
            action_counts = {}
            for action in AuditAction:
                count = query.filter(AuditLog.action == action).count()
                action_counts[action.value] = count
            
            # Top users
            top_users = (
                query.filter(AuditLog.user_id.isnot(None))
                .with_entities(AuditLog.user_id, func.count(AuditLog.id).label('count'))
                .group_by(AuditLog.user_id)
                .order_by(desc('count'))
                .limit(10)
                .all()
            )
            
            # Top resources
            top_resources = (
                query.with_entities(
                    AuditLog.resource_type,
                    func.count(AuditLog.id).label('count')
                )
                .group_by(AuditLog.resource_type)
                .order_by(desc('count'))
                .limit(10)
                .all()
            )
            
            return {
                "period": {
                    "start_time": start_time,
                    "end_time": end_time
                },
                "total_count": total_count,
                "status_counts": status_counts,
                "level_counts": level_counts,
                "action_counts": action_counts,
                "top_users": [{
                    "user_id": str(user_id),
                    "count": count
                } for user_id, count in top_users],
                "top_resources": [{
                    "resource_type": resource_type,
                    "count": count
                } for resource_type, count in top_resources]
            }
        except Exception as e:
            self.handle_db_error(e, "get audit statistics")
    
    def cleanup_old_logs(self, days_to_keep: int = 90) -> int:
        """Clean up old audit logs."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days_to_keep)
            
            # Count logs to be deleted
            count = self.db.query(AuditLog).filter(
                AuditLog.timestamp < cutoff_date
            ).count()
            
            # Delete old logs
            self.db.query(AuditLog).filter(
                AuditLog.timestamp < cutoff_date
            ).delete()
            
            self.db.commit()
            
            self.log_operation("cleanup_audit_logs", {
                "cutoff_date": cutoff_date,
                "deleted_count": count
            })
            
            return count
        except Exception as e:
            self.db.rollback()
            self.handle_db_error(e, "cleanup audit logs")
    
    def create_audit_trail(self, trail_data: AuditTrailCreateSchema) -> AuditTrail:
        """Create a new audit trail."""
        try:
            # Validate input
            trail_data = self.validate_input(trail_data, AuditTrailCreateSchema)
            
            # Create trail data
            create_data = {
                "id": uuid4(),
                "name": trail_data.name,
                "description": trail_data.description,
                "user_id": trail_data.user_id,
                "session_id": trail_data.session_id,
                "application_id": trail_data.application_id,
                "correlation_id": trail_data.correlation_id,
                "trace_id": trail_data.trace_id,
                "tags": trail_data.tags or [],
                "metadata": trail_data.metadata or {},
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create audit trail
            trail = AuditTrail(**create_data)
            self.db.add(trail)
            self.db.commit()
            self.db.refresh(trail)
            
            self.log_operation("create_audit_trail", {
                "trail_id": trail.id,
                "name": trail.name
            })
            
            return trail
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create audit trail")
    
    def add_log_to_trail(self, trail_id: UUID, audit_log_id: UUID) -> AuditTrailEntry:
        """Add an audit log to a trail."""
        try:
            # Check if trail exists
            trail = self.db.query(AuditTrail).filter(AuditTrail.id == trail_id).first()
            if not trail:
                raise NotFoundError("AuditTrail", trail_id)
            
            # Check if audit log exists
            audit_log = self.audit_crud.get(audit_log_id)
            if not audit_log:
                raise NotFoundError("AuditLog", audit_log_id)
            
            # Create trail entry
            entry = AuditTrailEntry(
                id=uuid4(),
                trail_id=trail_id,
                audit_log_id=audit_log_id,
                created_at=datetime.utcnow()
            )
            
            self.db.add(entry)
            self.db.commit()
            self.db.refresh(entry)
            
            return entry
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "add log to trail")
    
    def get_trail_logs(self, trail_id: UUID) -> List[AuditLog]:
        """Get all audit logs in a trail."""
        try:
            return (
                self.db.query(AuditLog)
                .join(AuditTrailEntry, AuditLog.id == AuditTrailEntry.audit_log_id)
                .filter(AuditTrailEntry.trail_id == trail_id)
                .order_by(AuditLog.timestamp)
                .all()
            )
        except Exception as e:
            self.handle_db_error(e, "get trail logs")
    
    # Convenience methods for common audit actions
    def log_login(self, user_id: UUID, session_id: UUID, client_info: Dict[str, str], success: bool = True) -> AuditLog:
        """Log user login action."""
        return self.log_action(
            action=AuditAction.LOGIN,
            resource_type="user",
            user_id=user_id,
            session_id=session_id,
            resource_id=str(user_id),
            level=AuditLevel.INFO,
            status=AuditStatus.SUCCESS if success else AuditStatus.FAILURE,
            message="User login" + (" successful" if success else " failed"),
            client_info=client_info
        )
    
    def log_logout(self, user_id: UUID, session_id: UUID, client_info: Dict[str, str]) -> AuditLog:
        """Log user logout action."""
        return self.log_action(
            action=AuditAction.LOGOUT,
            resource_type="user",
            user_id=user_id,
            session_id=session_id,
            resource_id=str(user_id),
            level=AuditLevel.INFO,
            status=AuditStatus.SUCCESS,
            message="User logout",
            client_info=client_info
        )
    
    def log_create(self, user_id: UUID, resource_type: str, resource_id: str, resource_name: str, new_values: Dict[str, Any]) -> AuditLog:
        """Log resource creation action."""
        return self.log_action(
            action=AuditAction.CREATE,
            resource_type=resource_type,
            user_id=user_id,
            resource_id=resource_id,
            resource_name=resource_name,
            level=AuditLevel.INFO,
            status=AuditStatus.SUCCESS,
            message=f"Created {resource_type}: {resource_name}",
            new_values=new_values
        )
    
    def log_update(self, user_id: UUID, resource_type: str, resource_id: str, resource_name: str, old_values: Dict[str, Any], new_values: Dict[str, Any], changed_fields: List[str]) -> AuditLog:
        """Log resource update action."""
        return self.log_action(
            action=AuditAction.UPDATE,
            resource_type=resource_type,
            user_id=user_id,
            resource_id=resource_id,
            resource_name=resource_name,
            level=AuditLevel.INFO,
            status=AuditStatus.SUCCESS,
            message=f"Updated {resource_type}: {resource_name}",
            old_values=old_values,
            new_values=new_values,
            changed_fields=changed_fields
        )
    
    def log_delete(self, user_id: UUID, resource_type: str, resource_id: str, resource_name: str, old_values: Dict[str, Any]) -> AuditLog:
        """Log resource deletion action."""
        return self.log_action(
            action=AuditAction.DELETE,
            resource_type=resource_type,
            user_id=user_id,
            resource_id=resource_id,
            resource_name=resource_name,
            level=AuditLevel.WARNING,
            status=AuditStatus.SUCCESS,
            message=f"Deleted {resource_type}: {resource_name}",
            old_values=old_values
        )
    
    def log_access(self, user_id: UUID, resource_type: str, resource_id: str, resource_name: str, action_details: str = None) -> AuditLog:
        """Log resource access action."""
        return self.log_action(
            action=AuditAction.ACCESS,
            resource_type=resource_type,
            user_id=user_id,
            resource_id=resource_id,
            resource_name=resource_name,
            level=AuditLevel.DEBUG,
            status=AuditStatus.SUCCESS,
            message=f"Accessed {resource_type}: {resource_name}",
            description=action_details
        )
    
    def log_error(self, user_id: UUID, resource_type: str, error_code: str, error_message: str, error_details: Dict[str, Any] = None) -> AuditLog:
        """Log error action."""
        return self.log_action(
            action=AuditAction.ERROR,
            resource_type=resource_type,
            user_id=user_id,
            level=AuditLevel.ERROR,
            status=AuditStatus.FAILURE,
            message=f"Error in {resource_type}: {error_message}",
            error_info={
                "code": error_code,
                "message": error_message,
                "details": error_details or {}
            }
        )