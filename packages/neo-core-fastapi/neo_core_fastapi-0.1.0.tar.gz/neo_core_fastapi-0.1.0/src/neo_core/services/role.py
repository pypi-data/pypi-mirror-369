"""Role and permission management services."""

from typing import List, Optional, Dict, Any, Union
from uuid import UUID, uuid4
from datetime import datetime

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func
from pydantic import BaseModel

from .base import BaseService, ServiceException, NotFoundError, ValidationException, DuplicateError
from .crud import RoleCRUDService, PermissionCRUDService, PermissionGroupCRUDService
from ..models.role import Role, RoleType, RoleStatus, RolePermission
from ..models.permission import Permission, PermissionGroup, PermissionType, PermissionScope, PermissionAction
from ..config import CoreSettings


class RoleCreateSchema(BaseModel):
    """Schema for creating a role."""
    name: str
    code: str
    description: Optional[str] = None
    type: RoleType = RoleType.CUSTOM
    status: RoleStatus = RoleStatus.ACTIVE
    is_system: bool = False
    is_default: bool = False
    parent_role_id: Optional[UUID] = None
    application_id: Optional[UUID] = None
    permission_ids: Optional[List[UUID]] = None
    priority: int = 0
    max_users: Optional[int] = None
    expires_at: Optional[datetime] = None


class RoleUpdateSchema(BaseModel):
    """Schema for updating a role."""
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[RoleStatus] = None
    is_default: Optional[bool] = None
    parent_role_id: Optional[UUID] = None
    permission_ids: Optional[List[UUID]] = None
    priority: Optional[int] = None
    max_users: Optional[int] = None
    expires_at: Optional[datetime] = None


class PermissionCreateSchema(BaseModel):
    """Schema for creating a permission."""
    name: str
    code: str
    description: Optional[str] = None
    resource: str
    action: PermissionAction
    type: PermissionType = PermissionType.FUNCTIONAL
    scope: PermissionScope = PermissionScope.GLOBAL
    parent_permission_id: Optional[UUID] = None
    application_id: Optional[UUID] = None
    conditions: Optional[Dict[str, Any]] = None
    priority: int = 0
    group_ids: Optional[List[UUID]] = None


class PermissionUpdateSchema(BaseModel):
    """Schema for updating a permission."""
    name: Optional[str] = None
    description: Optional[str] = None
    resource: Optional[str] = None
    action: Optional[PermissionAction] = None
    type: Optional[PermissionType] = None
    scope: Optional[PermissionScope] = None
    parent_permission_id: Optional[UUID] = None
    conditions: Optional[Dict[str, Any]] = None
    priority: Optional[int] = None
    group_ids: Optional[List[UUID]] = None


class PermissionGroupCreateSchema(BaseModel):
    """Schema for creating a permission group."""
    name: str
    code: str
    description: Optional[str] = None
    parent_group_id: Optional[UUID] = None
    application_id: Optional[UUID] = None
    sort_order: int = 0
    permission_ids: Optional[List[UUID]] = None


class PermissionGroupUpdateSchema(BaseModel):
    """Schema for updating a permission group."""
    name: Optional[str] = None
    description: Optional[str] = None
    parent_group_id: Optional[UUID] = None
    sort_order: Optional[int] = None
    permission_ids: Optional[List[UUID]] = None


class RoleService(BaseService):
    """Service for role management."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        self.role_crud = RoleCRUDService(settings)
        self.permission_crud = PermissionCRUDService(settings)
    
    def create_role(self, role_data: RoleCreateSchema) -> Role:
        """Create a new role."""
        try:
            # Validate input
            role_data = self.validate_input(role_data, RoleCreateSchema)
            
            # Check if role name already exists
            existing_role = self.role_crud.get_by_name(role_data.name)
            if existing_role:
                raise DuplicateError("Role", "name", role_data.name)
            
            # Check if role code already exists
            existing_role = self.role_crud.get_by_code(role_data.code)
            if existing_role:
                raise DuplicateError("Role", "code", role_data.code)
            
            # Validate parent role if specified
            if role_data.parent_role_id:
                parent_role = self.role_crud.get(role_data.parent_role_id)
                if not parent_role:
                    raise NotFoundError("Parent Role", role_data.parent_role_id)
                if not parent_role.is_active:
                    raise ValidationException("Parent role is not active")
            
            # Create role data
            create_data = {
                "id": uuid4(),
                "name": role_data.name,
                "code": role_data.code,
                "description": role_data.description,
                "type": role_data.type,
                "status": role_data.status,
                "is_system": role_data.is_system,
                "is_default": role_data.is_default,
                "parent_role_id": role_data.parent_role_id,
                "application_id": role_data.application_id,
                "priority": role_data.priority,
                "max_users": role_data.max_users,
                "expires_at": role_data.expires_at,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create role
            role = self.role_crud.create(create_data, commit=False)
            
            # Assign permissions if provided
            if role_data.permission_ids:
                permissions = []
                for permission_id in role_data.permission_ids:
                    permission = self.permission_crud.get(permission_id)
                    if permission and permission.is_active:
                        permissions.append(permission)
                role.permissions = permissions
            
            # Commit transaction
            self.db.commit()
            self.db.refresh(role)
            
            self.log_operation("create_role", {
                "role_id": role.id,
                "name": role.name,
                "code": role.code
            })
            
            return role
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create role")
    
    def get_role(self, role_id: UUID, include_permissions: bool = False) -> Optional[Role]:
        """Get a role by ID with optional permissions."""
        try:
            role = self.role_crud.get(role_id)
            if not role:
                return None
            
            # Load permissions if requested
            if include_permissions:
                role.permissions = self.permission_crud.get_permissions_by_role(role_id)
            
            return role
        except Exception as e:
            self.handle_db_error(e, "get role")
    
    def get_role_by_code(self, code: str) -> Optional[Role]:
        """Get a role by code."""
        return self.role_crud.get_by_code(code)
    
    def update_role(self, role_id: UUID, role_data: RoleUpdateSchema) -> Role:
        """Update a role."""
        try:
            # Validate input
            role_data = self.validate_input(role_data, RoleUpdateSchema)
            
            # Get existing role
            role = self.role_crud.get(role_id)
            if not role:
                raise NotFoundError("Role", role_id)
            
            # Check if it's a system role and prevent certain updates
            if role.is_system and role_data.name:
                raise ValidationException("Cannot change name of system role")
            
            # Check for name conflicts
            if role_data.name and role_data.name != role.name:
                existing_role = self.role_crud.get_by_name(role_data.name)
                if existing_role and existing_role.id != role_id:
                    raise DuplicateError("Role", "name", role_data.name)
            
            # Validate parent role if specified
            if role_data.parent_role_id:
                if role_data.parent_role_id == role_id:
                    raise ValidationException("Role cannot be its own parent")
                
                parent_role = self.role_crud.get(role_data.parent_role_id)
                if not parent_role:
                    raise NotFoundError("Parent Role", role_data.parent_role_id)
                if not parent_role.is_active:
                    raise ValidationException("Parent role is not active")
                
                # Check for circular dependency
                if self._would_create_circular_dependency(role_id, role_data.parent_role_id):
                    raise ValidationException("Would create circular dependency in role hierarchy")
            
            # Update role data
            update_data = role_data.dict(exclude_unset=True, exclude={"permission_ids"})
            
            # Update permissions if provided
            if role_data.permission_ids is not None:
                permissions = []
                for permission_id in role_data.permission_ids:
                    permission = self.permission_crud.get(permission_id)
                    if permission and permission.is_active:
                        permissions.append(permission)
                role.permissions = permissions
            
            # Update role
            updated_role = self.role_crud.update(role_id, update_data)
            
            self.log_operation("update_role", {
                "role_id": role_id,
                "updated_fields": list(update_data.keys())
            })
            
            return updated_role
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "update role")
    
    def delete_role(self, role_id: UUID, soft_delete: bool = True) -> bool:
        """Delete a role."""
        try:
            role = self.role_crud.get(role_id)
            if not role:
                raise NotFoundError("Role", role_id)
            
            # Prevent deletion of system roles
            if role.is_system:
                raise ValidationException("Cannot delete system role")
            
            # Check if role has users assigned
            if role.users:
                raise ValidationException("Cannot delete role with assigned users")
            
            # Perform deletion
            result = self.role_crud.delete(role_id, soft_delete=soft_delete)
            
            self.log_operation("delete_role", {
                "role_id": role_id,
                "soft_delete": soft_delete
            })
            
            return result
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "delete role")
    
    def list_roles(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        order_by: str = "name",
        order_desc: bool = False
    ) -> List[Role]:
        """List roles with filtering and pagination."""
        return self.role_crud.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=order_by,
            order_desc=order_desc
        )
    
    def get_role_hierarchy(self, role_id: UUID) -> List[Role]:
        """Get role hierarchy (parent and child roles)."""
        return self.role_crud.get_role_hierarchy(role_id)
    
    def assign_permission(self, role_id: UUID, permission_id: UUID) -> Role:
        """Assign a permission to a role."""
        try:
            role = self.role_crud.get(role_id)
            if not role:
                raise NotFoundError("Role", role_id)
            
            permission = self.permission_crud.get(permission_id)
            if not permission:
                raise NotFoundError("Permission", permission_id)
            
            if permission not in role.permissions:
                role.permissions.append(permission)
                self.db.commit()
                self.db.refresh(role)
            
            self.log_operation("assign_permission", {
                "role_id": role_id,
                "permission_id": permission_id
            })
            
            return role
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "assign permission")
    
    def revoke_permission(self, role_id: UUID, permission_id: UUID) -> Role:
        """Revoke a permission from a role."""
        try:
            role = self.role_crud.get(role_id)
            if not role:
                raise NotFoundError("Role", role_id)
            
            permission = self.permission_crud.get(permission_id)
            if not permission:
                raise NotFoundError("Permission", permission_id)
            
            if permission in role.permissions:
                role.permissions.remove(permission)
                self.db.commit()
                self.db.refresh(role)
            
            self.log_operation("revoke_permission", {
                "role_id": role_id,
                "permission_id": permission_id
            })
            
            return role
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "revoke permission")
    
    def _would_create_circular_dependency(self, role_id: UUID, parent_role_id: UUID) -> bool:
        """Check if setting parent would create circular dependency."""
        try:
            current_role_id = parent_role_id
            visited = set()
            
            while current_role_id and current_role_id not in visited:
                if current_role_id == role_id:
                    return True
                
                visited.add(current_role_id)
                parent_role = self.role_crud.get(current_role_id)
                current_role_id = parent_role.parent_role_id if parent_role else None
            
            return False
        except Exception:
            return True  # Assume circular dependency on error


class PermissionService(BaseService):
    """Service for permission management."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        self.permission_crud = PermissionCRUDService(settings)
        self.group_crud = PermissionGroupCRUDService(settings)
    
    def create_permission(self, permission_data: PermissionCreateSchema) -> Permission:
        """Create a new permission."""
        try:
            # Validate input
            permission_data = self.validate_input(permission_data, PermissionCreateSchema)
            
            # Check if permission code already exists
            existing_permission = self.permission_crud.get_by_code(permission_data.code)
            if existing_permission:
                raise DuplicateError("Permission", "code", permission_data.code)
            
            # Check if permission with same resource and action exists
            existing_permission = self.permission_crud.get_by_resource_action(
                permission_data.resource, permission_data.action
            )
            if existing_permission:
                raise DuplicateError(
                    "Permission",
                    "resource_action",
                    f"{permission_data.resource}:{permission_data.action}"
                )
            
            # Validate parent permission if specified
            if permission_data.parent_permission_id:
                parent_permission = self.permission_crud.get(permission_data.parent_permission_id)
                if not parent_permission:
                    raise NotFoundError("Parent Permission", permission_data.parent_permission_id)
                if not parent_permission.is_active:
                    raise ValidationException("Parent permission is not active")
            
            # Create permission data
            create_data = {
                "id": uuid4(),
                "name": permission_data.name,
                "code": permission_data.code,
                "description": permission_data.description,
                "resource": permission_data.resource,
                "action": permission_data.action,
                "type": permission_data.type,
                "scope": permission_data.scope,
                "parent_permission_id": permission_data.parent_permission_id,
                "application_id": permission_data.application_id,
                "conditions": permission_data.conditions,
                "priority": permission_data.priority,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create permission
            permission = self.permission_crud.create(create_data, commit=False)
            
            # Assign to groups if provided
            if permission_data.group_ids:
                groups = []
                for group_id in permission_data.group_ids:
                    group = self.group_crud.get(group_id)
                    if group and group.is_active:
                        groups.append(group)
                permission.groups = groups
            
            # Commit transaction
            self.db.commit()
            self.db.refresh(permission)
            
            self.log_operation("create_permission", {
                "permission_id": permission.id,
                "name": permission.name,
                "code": permission.code
            })
            
            return permission
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create permission")
    
    def get_permission(self, permission_id: UUID) -> Optional[Permission]:
        """Get a permission by ID."""
        return self.permission_crud.get(permission_id)
    
    def get_permission_by_code(self, code: str) -> Optional[Permission]:
        """Get a permission by code."""
        return self.permission_crud.get_by_code(code)
    
    def update_permission(self, permission_id: UUID, permission_data: PermissionUpdateSchema) -> Permission:
        """Update a permission."""
        try:
            # Validate input
            permission_data = self.validate_input(permission_data, PermissionUpdateSchema)
            
            # Get existing permission
            permission = self.permission_crud.get(permission_id)
            if not permission:
                raise NotFoundError("Permission", permission_id)
            
            # Check for resource/action conflicts
            if permission_data.resource or permission_data.action:
                resource = permission_data.resource or permission.resource
                action = permission_data.action or permission.action
                
                existing_permission = self.permission_crud.get_by_resource_action(resource, action)
                if existing_permission and existing_permission.id != permission_id:
                    raise DuplicateError("Permission", "resource_action", f"{resource}:{action}")
            
            # Validate parent permission if specified
            if permission_data.parent_permission_id:
                if permission_data.parent_permission_id == permission_id:
                    raise ValidationException("Permission cannot be its own parent")
                
                parent_permission = self.permission_crud.get(permission_data.parent_permission_id)
                if not parent_permission:
                    raise NotFoundError("Parent Permission", permission_data.parent_permission_id)
                if not parent_permission.is_active:
                    raise ValidationException("Parent permission is not active")
            
            # Update permission data
            update_data = permission_data.dict(exclude_unset=True, exclude={"group_ids"})
            
            # Update groups if provided
            if permission_data.group_ids is not None:
                groups = []
                for group_id in permission_data.group_ids:
                    group = self.group_crud.get(group_id)
                    if group and group.is_active:
                        groups.append(group)
                permission.groups = groups
            
            # Update permission
            updated_permission = self.permission_crud.update(permission_id, update_data)
            
            self.log_operation("update_permission", {
                "permission_id": permission_id,
                "updated_fields": list(update_data.keys())
            })
            
            return updated_permission
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "update permission")
    
    def delete_permission(self, permission_id: UUID, soft_delete: bool = True) -> bool:
        """Delete a permission."""
        try:
            permission = self.permission_crud.get(permission_id)
            if not permission:
                raise NotFoundError("Permission", permission_id)
            
            # Check if permission is assigned to roles
            roles_with_permission = self.db.query(Role).join(Role.permissions).filter(
                Permission.id == permission_id
            ).all()
            
            if roles_with_permission:
                raise ValidationException("Cannot delete permission assigned to roles")
            
            # Perform deletion
            result = self.permission_crud.delete(permission_id, soft_delete=soft_delete)
            
            self.log_operation("delete_permission", {
                "permission_id": permission_id,
                "soft_delete": soft_delete
            })
            
            return result
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "delete permission")
    
    def list_permissions(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        order_by: str = "name",
        order_desc: bool = False
    ) -> List[Permission]:
        """List permissions with filtering and pagination."""
        return self.permission_crud.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=order_by,
            order_desc=order_desc
        )
    
    def get_permissions_by_role(self, role_id: UUID) -> List[Permission]:
        """Get permissions by role."""
        return self.permission_crud.get_permissions_by_role(role_id)
    
    def get_permissions_by_group(self, group_id: UUID) -> List[Permission]:
        """Get permissions by group."""
        return self.permission_crud.get_permissions_by_group(group_id)


class PermissionGroupService(BaseService):
    """Service for permission group management."""
    
    def __init__(self, settings: CoreSettings = None):
        super().__init__(settings)
        self.group_crud = PermissionGroupCRUDService(settings)
        self.permission_crud = PermissionCRUDService(settings)
    
    def create_group(self, group_data: PermissionGroupCreateSchema) -> PermissionGroup:
        """Create a new permission group."""
        try:
            # Validate input
            group_data = self.validate_input(group_data, PermissionGroupCreateSchema)
            
            # Check if group code already exists
            existing_group = self.group_crud.get_by_code(group_data.code)
            if existing_group:
                raise DuplicateError("PermissionGroup", "code", group_data.code)
            
            # Validate parent group if specified
            if group_data.parent_group_id:
                parent_group = self.group_crud.get(group_data.parent_group_id)
                if not parent_group:
                    raise NotFoundError("Parent Group", group_data.parent_group_id)
                if not parent_group.is_active:
                    raise ValidationException("Parent group is not active")
            
            # Create group data
            create_data = {
                "id": uuid4(),
                "name": group_data.name,
                "code": group_data.code,
                "description": group_data.description,
                "parent_group_id": group_data.parent_group_id,
                "application_id": group_data.application_id,
                "sort_order": group_data.sort_order,
                "is_active": True,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Create group
            group = self.group_crud.create(create_data, commit=False)
            
            # Assign permissions if provided
            if group_data.permission_ids:
                permissions = []
                for permission_id in group_data.permission_ids:
                    permission = self.permission_crud.get(permission_id)
                    if permission and permission.is_active:
                        permissions.append(permission)
                group.permissions = permissions
            
            # Commit transaction
            self.db.commit()
            self.db.refresh(group)
            
            self.log_operation("create_group", {
                "group_id": group.id,
                "name": group.name,
                "code": group.code
            })
            
            return group
        except Exception as e:
            self.db.rollback()
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "create permission group")
    
    def get_group(self, group_id: UUID) -> Optional[PermissionGroup]:
        """Get a permission group by ID."""
        return self.group_crud.get(group_id)
    
    def update_group(self, group_id: UUID, group_data: PermissionGroupUpdateSchema) -> PermissionGroup:
        """Update a permission group."""
        try:
            # Validate input
            group_data = self.validate_input(group_data, PermissionGroupUpdateSchema)
            
            # Get existing group
            group = self.group_crud.get(group_id)
            if not group:
                raise NotFoundError("PermissionGroup", group_id)
            
            # Validate parent group if specified
            if group_data.parent_group_id:
                if group_data.parent_group_id == group_id:
                    raise ValidationException("Group cannot be its own parent")
                
                parent_group = self.group_crud.get(group_data.parent_group_id)
                if not parent_group:
                    raise NotFoundError("Parent Group", group_data.parent_group_id)
                if not parent_group.is_active:
                    raise ValidationException("Parent group is not active")
            
            # Update group data
            update_data = group_data.dict(exclude_unset=True, exclude={"permission_ids"})
            
            # Update permissions if provided
            if group_data.permission_ids is not None:
                permissions = []
                for permission_id in group_data.permission_ids:
                    permission = self.permission_crud.get(permission_id)
                    if permission and permission.is_active:
                        permissions.append(permission)
                group.permissions = permissions
            
            # Update group
            updated_group = self.group_crud.update(group_id, update_data)
            
            self.log_operation("update_group", {
                "group_id": group_id,
                "updated_fields": list(update_data.keys())
            })
            
            return updated_group
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "update permission group")
    
    def delete_group(self, group_id: UUID, soft_delete: bool = True) -> bool:
        """Delete a permission group."""
        try:
            group = self.group_crud.get(group_id)
            if not group:
                raise NotFoundError("PermissionGroup", group_id)
            
            # Check if group has child groups
            child_groups = self.group_crud.get_multi(filters={"parent_group_id": group_id})
            if child_groups:
                raise ValidationException("Cannot delete group with child groups")
            
            # Perform deletion
            result = self.group_crud.delete(group_id, soft_delete=soft_delete)
            
            self.log_operation("delete_group", {
                "group_id": group_id,
                "soft_delete": soft_delete
            })
            
            return result
        except Exception as e:
            if isinstance(e, ServiceException):
                raise
            self.handle_db_error(e, "delete permission group")
    
    def list_groups(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        order_by: str = "sort_order",
        order_desc: bool = False
    ) -> List[PermissionGroup]:
        """List permission groups with filtering and pagination."""
        return self.group_crud.get_multi(
            skip=skip,
            limit=limit,
            filters=filters,
            order_by=order_by,
            order_desc=order_desc
        )