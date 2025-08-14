"""Permission models for fine-grained access control."""

from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum

from sqlalchemy import Column, String, Boolean, DateTime, Text, Integer, ForeignKey, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from ..database.base import BaseModel
from ..database.mixins import TimestampMixin, SoftDeleteMixin, AuditMixin


class PermissionType(str, Enum):
    """Permission type enumeration."""
    SYSTEM = "system"  # System-level permissions
    APPLICATION = "application"  # Application-level permissions
    RESOURCE = "resource"  # Resource-specific permissions
    OPERATION = "operation"  # Operation-specific permissions
    DATA = "data"  # Data access permissions
    API = "api"  # API access permissions


class PermissionScope(str, Enum):
    """Permission scope enumeration."""
    GLOBAL = "global"  # Global scope
    APPLICATION = "application"  # Application scope
    MODULE = "module"  # Module scope
    RESOURCE = "resource"  # Resource scope
    RECORD = "record"  # Record-level scope


class PermissionAction(str, Enum):
    """Common permission actions."""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    EXECUTE = "execute"
    MANAGE = "manage"
    ADMIN = "admin"
    VIEW = "view"
    EDIT = "edit"
    APPROVE = "approve"
    REJECT = "reject"


# Association table for permission groups (many-to-many)
permission_group_permissions = Table(
    'permission_group_permissions',
    BaseModel.metadata,
    Column('group_id', UUID(as_uuid=True), ForeignKey('permission_group.id'), primary_key=True),
    Column('permission_id', UUID(as_uuid=True), ForeignKey('permission.id'), primary_key=True),
    Column('added_at', DateTime(timezone=True), default=datetime.utcnow),
    Column('added_by', UUID(as_uuid=True), nullable=True),
)


class Permission(BaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Permission model for fine-grained access control."""
    
    __tablename__ = "permission"
    
    # Basic information
    name = Column(
        String(200),
        unique=True,
        nullable=False,
        index=True,
        comment="Permission name (unique identifier)"
    )
    
    display_name = Column(
        String(300),
        nullable=True,
        comment="Human-readable permission name"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Permission description"
    )
    
    # Permission classification
    permission_type = Column(
        String(20),
        default=PermissionType.RESOURCE,
        nullable=False,
        comment="Permission type"
    )
    
    scope = Column(
        String(20),
        default=PermissionScope.APPLICATION,
        nullable=False,
        comment="Permission scope"
    )
    
    action = Column(
        String(50),
        nullable=False,
        comment="Permission action"
    )
    
    resource = Column(
        String(100),
        nullable=True,
        comment="Target resource"
    )
    
    # Hierarchy and grouping
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permission.id"),
        nullable=True,
        comment="Parent permission ID for hierarchy"
    )
    
    category = Column(
        String(100),
        nullable=True,
        comment="Permission category"
    )
    
    # Security and constraints
    is_system_permission = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="System permission flag (cannot be deleted)"
    )
    
    is_dangerous = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Dangerous permission flag (requires special handling)"
    )
    
    requires_approval = Column(
        Boolean,
        default=False,
        nullable=False,
        comment="Requires approval before granting"
    )
    
    # Application context
    application_id = Column(
        UUID(as_uuid=True),
        ForeignKey("application.id"),
        nullable=True,
        comment="Associated application ID"
    )
    
    module_name = Column(
        String(100),
        nullable=True,
        comment="Associated module name"
    )
    
    # Conditions and constraints
    conditions = Column(
        JSONB,
        nullable=True,
        comment="Permission conditions and constraints"
    )
    
    # Priority and ordering
    priority = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Permission priority"
    )
    
    # Additional metadata
    metadata = Column(
        JSONB,
        nullable=True,
        comment="Additional permission metadata"
    )
    
    tags = Column(
        String(500),
        nullable=True,
        comment="Comma-separated tags"
    )
    
    # Relationships
    parent = relationship(
        "Permission",
        remote_side="Permission.id",
        back_populates="children"
    )
    
    children = relationship(
        "Permission",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    
    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="dynamic"
    )
    
    groups = relationship(
        "PermissionGroup",
        secondary=permission_group_permissions,
        back_populates="permissions",
        lazy="dynamic"
    )
    
    application = relationship(
        "Application",
        back_populates="permissions"
    )
    
    def __repr__(self) -> str:
        return f"<Permission(id={self.id}, name={self.name}, action={self.action})>"
    
    @property
    def is_active(self) -> bool:
        """Check if permission is active."""
        return not self.is_deleted and self.is_active
    
    @property
    def full_name(self) -> str:
        """Get full permission name including resource and action."""
        parts = []
        if self.resource:
            parts.append(self.resource)
        parts.append(self.action)
        return ":".join(parts)
    
    @property
    def hierarchy_level(self) -> int:
        """Get permission hierarchy level."""
        level = 0
        current = self.parent
        while current:
            level += 1
            current = current.parent
        return level
    
    def get_all_children(self) -> List['Permission']:
        """Get all child permissions recursively."""
        all_children = []
        
        def collect_children(permission):
            for child in permission.children:
                if not child.is_deleted:
                    all_children.append(child)
                    collect_children(child)
        
        collect_children(self)
        return all_children
    
    def get_all_parents(self) -> List['Permission']:
        """Get all parent permissions up to root."""
        parents = []
        current = self.parent
        while current:
            if not current.is_deleted:
                parents.append(current)
            current = current.parent
        return parents
    
    def implies(self, other_permission: 'Permission') -> bool:
        """Check if this permission implies another permission."""
        # A permission implies another if:
        # 1. It's the same permission
        if self.name == other_permission.name:
            return True
        
        # 2. It's a parent permission with broader scope
        if other_permission in self.get_all_children():
            return True
        
        # 3. It's a wildcard permission
        if self.action == "*" and self.resource == other_permission.resource:
            return True
        
        if self.resource == "*" and self.action == other_permission.action:
            return True
        
        # 4. Custom implication logic based on metadata
        if self.metadata and "implies" in self.metadata:
            implied_permissions = self.metadata.get("implies", [])
            if other_permission.name in implied_permissions:
                return True
        
        return False
    
    def check_conditions(self, context: Dict[str, Any] = None) -> bool:
        """Check if permission conditions are met."""
        if not self.conditions:
            return True
        
        context = context or {}
        
        # Implement condition checking logic
        # This is a placeholder for custom condition evaluation
        # You can implement time-based, IP-based, or other conditions here
        
        return True
    
    def can_be_granted_to_role(self, role) -> tuple[bool, str]:
        """Check if permission can be granted to role."""
        if not self.is_active:
            return False, "Permission is not active"
        
        if self.requires_approval:
            return False, "Permission requires approval process"
        
        if self.is_dangerous and not role.is_system_role:
            return False, "Dangerous permission can only be granted to system roles"
        
        return True, "OK"
    
    @classmethod
    def create_crud_permissions(cls, resource_name: str, application_id=None) -> List['Permission']:
        """Create standard CRUD permissions for a resource."""
        permissions = []
        actions = ["create", "read", "update", "delete"]
        
        for action in actions:
            permission = cls(
                name=f"{resource_name}:{action}",
                display_name=f"{action.title()} {resource_name.title()}",
                description=f"Permission to {action} {resource_name} records",
                action=action,
                resource=resource_name,
                application_id=application_id
            )
            permissions.append(permission)
        
        return permissions
    
    @classmethod
    def create_wildcard_permission(cls, resource_name: str, application_id=None) -> 'Permission':
        """Create wildcard permission for a resource."""
        return cls(
            name=f"{resource_name}:*",
            display_name=f"Full Access to {resource_name.title()}",
            description=f"Full access permission for {resource_name} resource",
            action="*",
            resource=resource_name,
            application_id=application_id,
            is_dangerous=True
        )


class PermissionGroup(BaseModel, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """Permission group model for organizing related permissions."""
    
    __tablename__ = "permission_group"
    
    # Basic information
    name = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="Group name (unique)"
    )
    
    display_name = Column(
        String(200),
        nullable=True,
        comment="Human-readable group name"
    )
    
    description = Column(
        Text,
        nullable=True,
        comment="Group description"
    )
    
    # Group properties
    category = Column(
        String(100),
        nullable=True,
        comment="Group category"
    )
    
    color = Column(
        String(7),
        nullable=True,
        comment="Group color (hex code)"
    )
    
    icon = Column(
        String(50),
        nullable=True,
        comment="Group icon identifier"
    )
    
    # Hierarchy
    parent_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permission_group.id"),
        nullable=True,
        comment="Parent group ID"
    )
    
    # Ordering
    sort_order = Column(
        Integer,
        default=0,
        nullable=False,
        comment="Sort order within parent group"
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
        comment="Additional group metadata"
    )
    
    # Relationships
    parent = relationship(
        "PermissionGroup",
        remote_side="PermissionGroup.id",
        back_populates="children"
    )
    
    children = relationship(
        "PermissionGroup",
        back_populates="parent",
        cascade="all, delete-orphan"
    )
    
    permissions = relationship(
        "Permission",
        secondary=permission_group_permissions,
        back_populates="groups",
        lazy="dynamic"
    )
    
    application = relationship(
        "Application",
        back_populates="permission_groups"
    )
    
    def __repr__(self) -> str:
        return f"<PermissionGroup(id={self.id}, name={self.name})>"
    
    @property
    def is_active(self) -> bool:
        """Check if permission group is active."""
        return not self.is_deleted
    
    @property
    def permission_count(self) -> int:
        """Get number of permissions in group."""
        return self.permissions.count()
    
    @property
    def hierarchy_level(self) -> int:
        """Get group hierarchy level."""
        level = 0
        current = self.parent
        while current:
            level += 1
            current = current.parent
        return level
    
    def get_all_permissions(self, include_children: bool = True) -> List[Permission]:
        """Get all permissions in group and optionally child groups."""
        permissions = list(self.permissions.filter(Permission.is_deleted == False))
        
        if include_children:
            for child_group in self.children:
                if not child_group.is_deleted:
                    permissions.extend(child_group.get_all_permissions(include_children=True))
        
        return permissions
    
    def add_permission(self, permission: Permission, added_by=None) -> None:
        """Add permission to group."""
        if permission not in self.permissions:
            from sqlalchemy import insert
            from ..database.session import get_database_manager
            
            db_manager = get_database_manager()
            with db_manager.get_session() as session:
                stmt = insert(permission_group_permissions).values(
                    group_id=self.id,
                    permission_id=permission.id,
                    added_by=added_by
                )
                session.execute(stmt)
    
    def remove_permission(self, permission: Permission) -> None:
        """Remove permission from group."""
        if permission in self.permissions:
            self.permissions.remove(permission)
    
    def get_all_children(self) -> List['PermissionGroup']:
        """Get all child groups recursively."""
        all_children = []
        
        def collect_children(group):
            for child in group.children:
                if not child.is_deleted:
                    all_children.append(child)
                    collect_children(child)
        
        collect_children(self)
        return all_children
    
    def get_all_parents(self) -> List['PermissionGroup']:
        """Get all parent groups up to root."""
        parents = []
        current = self.parent
        while current:
            if not current.is_deleted:
                parents.append(current)
            current = current.parent
        return parents
    
    def move_to_parent(self, new_parent: Optional['PermissionGroup']) -> None:
        """Move group to new parent."""
        # Prevent circular references
        if new_parent and (new_parent == self or new_parent in self.get_all_children()):
            raise ValueError("Cannot move group to itself or its child")
        
        self.parent = new_parent
        self.parent_id = new_parent.id if new_parent else None