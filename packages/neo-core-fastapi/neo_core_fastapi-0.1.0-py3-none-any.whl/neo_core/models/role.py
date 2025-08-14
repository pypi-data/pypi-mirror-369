"""Role models for role-based access control."""

from datetime import datetime
from typing import Optional, List
from enum import Enum

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ..database.base import BaseModel
from ..database.mixins import TimestampMixin, SoftDeleteMixin, AuditMixin


class RoleType(str, Enum):
    """Role type enumeration."""
    SYSTEM = "system"  # System-defined roles
    CUSTOM = "custom"  # User-defined roles
    TEMPORARY = "temporary"  # Temporary roles
    GROUP = "group"  # Group-based roles


class RoleStatus(str, Enum):
    """Role status enumeration."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    DEPRECATED = "deprecated"
    DRAFT = "draft"


# Association table for role permissions (many-to-many)
role_permissions = Table(
    'role_permissions',
    BaseModel.metadata,
    Column('role_id', UUID(as_uuid=True), ForeignKey('role.id'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permission.id'), primary_key=True),
    Column('granted_at', DateTime(timezone=True), default=datetime.utcnow),
    Column('granted_by', UUID(as_uuid=True), nullable=True),
    Column('expires_at', DateTime(timezone=True), nullable=True),
    Column('conditions', JSONB, nullable=True),  # Additional conditions for permission
)


# Association table for role hierarchy (self-referencing many-to-many)
role_hierarchy = Table(
    'role_hierarchy',
    BaseModel.metadata,
    Column('parent_role_id', UUID(as_uuid=True), ForeignKey('role.id'), primary_key=True),
    Column('child_role_id', UUID(as_uuid=True), ForeignKey('role.id'), primary_key=True),
    Column('created_at', DateTime(timezone=True), default=datetime.utcnow),
    Column('created_by', UUID(as_uuid=True), nullable=True),
)


class Role(BaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Role model for role-based access control."""
    
    __tablename__ = "role"
    
    # Basic information
    name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Role name (unique)"
    )
    
    display_name = Column(
        String(200),
        nullable=True,
        comment="Human-readable role name"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Role description"
    )
    
    # Role properties
    role_type = Column(
        String(20),
        default=RoleType.CUSTOM,
        nullable=False,
        comment="Role type"
    )
    
    status = Column(
        String(20),
        default=RoleStatus.ACTIVE,
        nullable=False,
        comment="Role status"
    )
    
    # Hierarchy and priority
    priority = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Role priority (higher number = higher priority)"
    )
    
    level = Column(
        Integer,
        default=1,
        nullable=False,
        comment="Role level in hierarchy"
    )
    
    # Security settings
    is_system_role = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="System role flag (cannot be deleted)"
    )
    
    is_assignable = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Can be assigned to users"
    )
    
    is_inheritable = Column(
        Boolean,
        default=True,
        nullable=False,
        comment="Can inherit permissions from parent roles"
    )
    
    # Constraints
    max_users = Column(
        Integer,
        nullable=True,
        comment="Maximum number of users that can have this role"
    )
    
    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Role expiration date"
    )
    
    # Application context
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("application.id"),
        nullable=True,
        comment="Associated application ID"
    )
    
    # Additional metadata
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional role metadata"
    )
    
    tags = Column(
        String(500),
        nullable=True,
        comment="Comma-separated tags"
    )
    
    # Relationships
    users = relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        lazy="dynamic"
    )
    
    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="dynamic"
    )
    
    # Self-referencing relationship for role hierarchy
    parent_roles = relationship(
        "Role",
        secondary=role_hierarchy,
        primaryjoin="Role.id == role_hierarchy.c.child_role_id",
        secondaryjoin="Role.id == role_hierarchy.c.parent_role_id",
        back_populates="child_roles",
        lazy="dynamic"
    )
    
    child_roles = relationship(
        "Role",
        secondary=role_hierarchy,
        primaryjoin="Role.id == role_hierarchy.c.parent_role_id",
        secondaryjoin="Role.id == role_hierarchy.c.child_role_id",
        back_populates="parent_roles",
        lazy="dynamic"
    )
    
    application = relationship(
        "Application",
        back_populates="roles"
    )
    
    def __repr__(self) -> str:
        return f"<Role(id={self.id}, name={self.name}, type={self.role_type})>"
    
    @property
    def is_active(self) -> bool:
        """Check if role is active."""
        if self.is_deleted:
            return False
        
        if self.status != RoleStatus.ACTIVE:
            return False
        
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        
        return True
    
    @property
    def user_count(self) -> int:
        """Get number of users with this role."""
        return self.users.count()
    
    @property
    def permission_count(self) -> int:
        """Get number of permissions for this role."""
        return self.permissions.count()
    
    @property
    def effective_permissions(self) -> List[str]:
        """Get all effective permissions including inherited ones."""
        permissions = set()
        
        # Add direct permissions
        for permission in self.permissions:
            if permission.is_active:
                permissions.add(permission.name)
        
        # Add inherited permissions if inheritable
        if self.is_inheritable:
            for parent_role in self.parent_roles:
                if parent_role.is_active:
                    permissions.update(parent_role.effective_permissions)
        
        return list(permissions)
    
    def has_permission(self, permission_name: str) -> bool:
        """Check if role has specific permission."""
        return permission_name in self.effective_permissions
    
    def add_permission(self, permission, granted_by=None, expires_at=None, conditions=None):
        """Add permission to role."""
        if permission not in self.permissions:
            # Use the association table to add additional metadata
            from sqlalchemy import insert
            from ..database.session import get_database_manager
            
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                stmt = insert(role_permissions).values(
                    role_id=self.id,
                    permission_id=permission.id,
                    granted_by=granted_by,
                    expires_at=expires_at,
                    conditions=conditions
                )
                session.execute(stmt)
    
    def remove_permission(self, permission):
        """Remove permission from role."""
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def add_parent_role(self, parent_role, created_by=None):
        """Add parent role to create hierarchy."""
        if parent_role not in self.parent_roles and parent_role != self:
            # Prevent circular dependencies
            if not self._would_create_cycle(parent_role):
                from sqlalchemy import insert
                from ..database.session import get_database_manager
                
                db_manager = get_database_manager()
                with db_manager.get_session() as session:
                    stmt = insert(role_hierarchy).values(
                        parent_role_id=parent_role.id,
                        child_role_id=self.id,
                        created_by=created_by
                    )
                    session.execute(stmt)
    
    def remove_parent_role(self, parent_role):
        """Remove parent role from hierarchy."""
        if parent_role in self.parent_roles:
            self.parent_roles.remove(parent_role)
    
    def _would_create_cycle(self, potential_parent) -> bool:
        """Check if adding parent would create circular dependency."""
        visited = set()
        
        def check_cycle(role):
            if role.id in visited:
                return True
            visited.add(role.id)
            
            for child in role.child_roles:
                if child.id == self.id or check_cycle(child):
                    return True
            
            return False
        
        return check_cycle(potential_parent)
    
    def can_assign_to_user(self, user) -> tuple[bool, str]:
        """Check if role can be assigned to user."""
        if not self.is_active:
            return False, "Role is not active"
        
        if not self.is_assignable:
            return False, "Role is not assignable"
        
        if self.max_users and self.user_count >= self.max_users:
            return False, "Role has reached maximum user limit"
        
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False, "Role has expired"
        
        return True, "OK"
    
    def activate(self) -> None:
        """Activate role."""
        self.status = RoleStatus.ACTIVE
    
    def deactivate(self) -> None:
        """Deactivate role."""
        self.status = RoleStatus.INACTIVE
    
    def deprecate(self) -> None:
        """Mark role as deprecated."""
        self.status = RoleStatus.DEPRECATED
        self.is_assignable = False
    
    def get_all_child_roles(self) -> List['Role']:
        """Get all child roles recursively."""
        all_children = []
        visited = set()
        
        def collect_children(role):
            if role.id in visited:
                return
            visited.add(role.id)
            
            for child in role.child_roles:
                if child.id not in visited:
                    all_children.append(child)
                    collect_children(child)
        
        collect_children(self)
        return all_children
    
    def get_all_parent_roles(self) -> List['Role']:
        """Get all parent roles recursively."""
        all_parents = []
        visited = set()
        
        def collect_parents(role):
            if role.id in visited:
                return
            visited.add(role.id)
            
            for parent in role.parent_roles:
                if parent.id not in visited:
                    all_parents.append(parent)
                    collect_parents(parent)
        
        collect_parents(self)
        return all_parents


class RolePermission(BaseModel, TimestampMixin):
    """Role permission association model with additional metadata."""
    
    __tablename__ = "role_permission"
    
    # Foreign keys
    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey("role.id"),
        nullable=False,
        comment="Role ID"
    )
    
    permission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permission.id"),
        nullable=False,
        comment="Permission ID"
    )
    
    # Grant information
    granted_by = Column(
        UUID(as_uuid=True),
        ForeignKey("user.id"),
        nullable=True,
        comment="User who granted the permission"
    )
    
    granted_at = Column(
        DateTime(timezone=True),
        default=datetime.utcnow,
        nullable=False,
        comment="When permission was granted"
    )
    
    expires_at = Column(
        DateTime(timezone=True),
        nullable=True,
        comment="Permission expiration date"
    )
    
    # Additional conditions
    conditions = Column(
        JSONB,
        nullable=True,
        comment="Additional conditions for permission usage"
    )
    
    is_inherited = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Whether this permission is inherited from parent role"
    )
    
    # Relationships
    role = relationship(
        "Role",
        foreign_keys=[role_id]
    )
    
    permission = relationship(
        "Permission",
        foreign_keys=[permission_id]
    )
    
    granted_by_user = relationship(
        "User",
        foreign_keys=[granted_by]
    )
    
    def __repr__(self) -> str:
        return f"<RolePermission(role_id={self.role_id}, permission_id={self.permission_id})>"
    
    @property
    def is_active(self) -> bool:
        """Check if role permission is active."""
        if self.expires_at and datetime.utcnow() > self.expires_at:
            return False
        return True
    
    def check_conditions(self, context: dict = None) -> bool:
        """Check if conditions are met for permission usage."""
        if not self.conditions:
            return True
        
        # Implement condition checking logic based on your requirements
        # This is a placeholder for custom condition evaluation
        return True