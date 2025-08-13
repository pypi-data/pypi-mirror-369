from tecton_proto.auditlog import metadata__client_pb2 as _metadata__client_pb2
from tecton_proto.auth import principal__client_pb2 as _principal__client_pb2
from tecton_proto.auth import resource__client_pb2 as _resource__client_pb2
from tecton_proto.auth import resource_role_assignments__client_pb2 as _resource_role_assignments__client_pb2
from tecton_proto.auth import service__client_pb2 as _service__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GetRolesRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetRolesResponse(_message.Message):
    __slots__ = ["roles"]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    roles: _containers.RepeatedCompositeFieldContainer[RoleDefinition]
    def __init__(self, roles: _Optional[_Iterable[_Union[RoleDefinition, _Mapping]]] = ...) -> None: ...

class RoleDefinition(_message.Message):
    __slots__ = ["id", "name", "description", "assignable_on_resource_types", "assignable_to_principal_types", "permissions", "legacy_id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ASSIGNABLE_ON_RESOURCE_TYPES_FIELD_NUMBER: _ClassVar[int]
    ASSIGNABLE_TO_PRINCIPAL_TYPES_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    LEGACY_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    assignable_on_resource_types: _containers.RepeatedScalarFieldContainer[_resource__client_pb2.ResourceType]
    assignable_to_principal_types: _containers.RepeatedScalarFieldContainer[_principal__client_pb2.PrincipalType]
    permissions: _containers.RepeatedCompositeFieldContainer[PermissionDefinition]
    legacy_id: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., assignable_on_resource_types: _Optional[_Iterable[_Union[_resource__client_pb2.ResourceType, str]]] = ..., assignable_to_principal_types: _Optional[_Iterable[_Union[_principal__client_pb2.PrincipalType, str]]] = ..., permissions: _Optional[_Iterable[_Union[PermissionDefinition, _Mapping]]] = ..., legacy_id: _Optional[str] = ...) -> None: ...

class PermissionDefinition(_message.Message):
    __slots__ = ["id", "description", "is_authorized"]
    ID_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IS_AUTHORIZED_FIELD_NUMBER: _ClassVar[int]
    id: str
    description: str
    is_authorized: bool
    def __init__(self, id: _Optional[str] = ..., description: _Optional[str] = ..., is_authorized: bool = ...) -> None: ...

class GetAssignedRolesRequest(_message.Message):
    __slots__ = ["principal_type", "principal_id", "resource_type", "resource_ids", "roles"]
    PRINCIPAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_IDS_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    principal_type: _principal__client_pb2.PrincipalType
    principal_id: str
    resource_type: _resource__client_pb2.ResourceType
    resource_ids: _containers.RepeatedScalarFieldContainer[str]
    roles: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, principal_type: _Optional[_Union[_principal__client_pb2.PrincipalType, str]] = ..., principal_id: _Optional[str] = ..., resource_type: _Optional[_Union[_resource__client_pb2.ResourceType, str]] = ..., resource_ids: _Optional[_Iterable[str]] = ..., roles: _Optional[_Iterable[str]] = ...) -> None: ...

class GetAssignedRolesResponse(_message.Message):
    __slots__ = ["assignments"]
    ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    assignments: _containers.RepeatedCompositeFieldContainer[_resource_role_assignments__client_pb2.ResourceAndRoleAssignments]
    def __init__(self, assignments: _Optional[_Iterable[_Union[_resource_role_assignments__client_pb2.ResourceAndRoleAssignments, _Mapping]]] = ...) -> None: ...

class ListAssignedRolesRequest(_message.Message):
    __slots__ = ["principal_type", "principal_id", "resource_type", "resource_ids", "roles"]
    PRINCIPAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_IDS_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    principal_type: _principal__client_pb2.PrincipalType
    principal_id: str
    resource_type: _resource__client_pb2.ResourceType
    resource_ids: _containers.RepeatedScalarFieldContainer[str]
    roles: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, principal_type: _Optional[_Union[_principal__client_pb2.PrincipalType, str]] = ..., principal_id: _Optional[str] = ..., resource_type: _Optional[_Union[_resource__client_pb2.ResourceType, str]] = ..., resource_ids: _Optional[_Iterable[str]] = ..., roles: _Optional[_Iterable[str]] = ...) -> None: ...

class ListAssignedRolesResponse(_message.Message):
    __slots__ = ["assignments"]
    ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    assignments: _containers.RepeatedCompositeFieldContainer[_resource_role_assignments__client_pb2.ResourceAndRoleAssignmentsV2]
    def __init__(self, assignments: _Optional[_Iterable[_Union[_resource_role_assignments__client_pb2.ResourceAndRoleAssignmentsV2, _Mapping]]] = ...) -> None: ...

class GetIsAuthorizedRequest(_message.Message):
    __slots__ = ["principal_type", "principal_id", "permissions"]
    PRINCIPAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_ID_FIELD_NUMBER: _ClassVar[int]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    principal_type: _principal__client_pb2.PrincipalType
    principal_id: str
    permissions: _containers.RepeatedCompositeFieldContainer[Permission]
    def __init__(self, principal_type: _Optional[_Union[_principal__client_pb2.PrincipalType, str]] = ..., principal_id: _Optional[str] = ..., permissions: _Optional[_Iterable[_Union[Permission, _Mapping]]] = ...) -> None: ...

class GetIsAuthorizedResponse(_message.Message):
    __slots__ = ["permissions"]
    PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    permissions: _containers.RepeatedCompositeFieldContainer[Permission]
    def __init__(self, permissions: _Optional[_Iterable[_Union[Permission, _Mapping]]] = ...) -> None: ...

class AssignRolesRequest(_message.Message):
    __slots__ = ["assignments"]
    ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    assignments: _containers.RepeatedCompositeFieldContainer[Assignment]
    def __init__(self, assignments: _Optional[_Iterable[_Union[Assignment, _Mapping]]] = ...) -> None: ...

class AssignRolesResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class UnassignRolesRequest(_message.Message):
    __slots__ = ["assignments"]
    ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    assignments: _containers.RepeatedCompositeFieldContainer[Assignment]
    def __init__(self, assignments: _Optional[_Iterable[_Union[Assignment, _Mapping]]] = ...) -> None: ...

class UnassignRolesResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class Assignment(_message.Message):
    __slots__ = ["resource_type", "resource_id", "role", "principal_type", "principal_id"]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_ID_FIELD_NUMBER: _ClassVar[int]
    resource_type: _resource__client_pb2.ResourceType
    resource_id: str
    role: str
    principal_type: _principal__client_pb2.PrincipalType
    principal_id: str
    def __init__(self, resource_type: _Optional[_Union[_resource__client_pb2.ResourceType, str]] = ..., resource_id: _Optional[str] = ..., role: _Optional[str] = ..., principal_type: _Optional[_Union[_principal__client_pb2.PrincipalType, str]] = ..., principal_id: _Optional[str] = ...) -> None: ...

class AssignRolesPutRequest(_message.Message):
    __slots__ = ["resource_type", "resource_id", "principal_type", "principal_id", "roles"]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_ID_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    resource_type: _resource__client_pb2.ResourceType
    resource_id: str
    principal_type: _principal__client_pb2.PrincipalType
    principal_id: str
    roles: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, resource_type: _Optional[_Union[_resource__client_pb2.ResourceType, str]] = ..., resource_id: _Optional[str] = ..., principal_type: _Optional[_Union[_principal__client_pb2.PrincipalType, str]] = ..., principal_id: _Optional[str] = ..., roles: _Optional[_Iterable[str]] = ...) -> None: ...

class AssignRolesPutResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetAuthorizedResourcesRequest(_message.Message):
    __slots__ = ["principal_type", "principal_id", "resource_type", "action"]
    PRINCIPAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    principal_type: _principal__client_pb2.PrincipalType
    principal_id: str
    resource_type: _resource__client_pb2.ResourceType
    action: str
    def __init__(self, principal_type: _Optional[_Union[_principal__client_pb2.PrincipalType, str]] = ..., principal_id: _Optional[str] = ..., resource_type: _Optional[_Union[_resource__client_pb2.ResourceType, str]] = ..., action: _Optional[str] = ...) -> None: ...

class GetAuthorizedResourcesResponse(_message.Message):
    __slots__ = ["authorized_resources"]
    AUTHORIZED_RESOURCES_FIELD_NUMBER: _ClassVar[int]
    authorized_resources: _containers.RepeatedCompositeFieldContainer[AuthorizedResources]
    def __init__(self, authorized_resources: _Optional[_Iterable[_Union[AuthorizedResources, _Mapping]]] = ...) -> None: ...

class AuthorizedResources(_message.Message):
    __slots__ = ["resource_id", "actions"]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    resource_id: str
    actions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, resource_id: _Optional[str] = ..., actions: _Optional[_Iterable[str]] = ...) -> None: ...

class GetAssignedPrincipalsRequest(_message.Message):
    __slots__ = ["resource_type", "resource_id", "roles", "principal_types"]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_TYPES_FIELD_NUMBER: _ClassVar[int]
    resource_type: _resource__client_pb2.ResourceType
    resource_id: str
    roles: _containers.RepeatedScalarFieldContainer[str]
    principal_types: _containers.RepeatedScalarFieldContainer[_principal__client_pb2.PrincipalType]
    def __init__(self, resource_type: _Optional[_Union[_resource__client_pb2.ResourceType, str]] = ..., resource_id: _Optional[str] = ..., roles: _Optional[_Iterable[str]] = ..., principal_types: _Optional[_Iterable[_Union[_principal__client_pb2.PrincipalType, str]]] = ...) -> None: ...

class GetAssignedPrincipalsResponse(_message.Message):
    __slots__ = ["assignments"]
    ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    assignments: _containers.RepeatedCompositeFieldContainer[AssignmentBasic]
    def __init__(self, assignments: _Optional[_Iterable[_Union[AssignmentBasic, _Mapping]]] = ...) -> None: ...

class ListAssignedPrincipalsRequest(_message.Message):
    __slots__ = ["resource_type", "resource_id", "roles", "principal_types"]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_TYPES_FIELD_NUMBER: _ClassVar[int]
    resource_type: _resource__client_pb2.ResourceType
    resource_id: str
    roles: _containers.RepeatedScalarFieldContainer[str]
    principal_types: _containers.RepeatedScalarFieldContainer[_principal__client_pb2.PrincipalType]
    def __init__(self, resource_type: _Optional[_Union[_resource__client_pb2.ResourceType, str]] = ..., resource_id: _Optional[str] = ..., roles: _Optional[_Iterable[str]] = ..., principal_types: _Optional[_Iterable[_Union[_principal__client_pb2.PrincipalType, str]]] = ...) -> None: ...

class ListAssignedPrincipalsResponse(_message.Message):
    __slots__ = ["assignments"]
    ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    assignments: _containers.RepeatedCompositeFieldContainer[AssignmentBasicV2]
    def __init__(self, assignments: _Optional[_Iterable[_Union[AssignmentBasicV2, _Mapping]]] = ...) -> None: ...

class AssignmentBasic(_message.Message):
    __slots__ = ["principal", "roles", "role_assignments"]
    PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    ROLES_FIELD_NUMBER: _ClassVar[int]
    ROLE_ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    principal: _principal__client_pb2.PrincipalBasic
    roles: _containers.RepeatedScalarFieldContainer[str]
    role_assignments: _containers.RepeatedCompositeFieldContainer[_resource_role_assignments__client_pb2.ResourceAndRoleAssignments]
    def __init__(self, principal: _Optional[_Union[_principal__client_pb2.PrincipalBasic, _Mapping]] = ..., roles: _Optional[_Iterable[str]] = ..., role_assignments: _Optional[_Iterable[_Union[_resource_role_assignments__client_pb2.ResourceAndRoleAssignments, _Mapping]]] = ...) -> None: ...

class AssignmentBasicV2(_message.Message):
    __slots__ = ["principal", "role_assignments"]
    PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    ROLE_ASSIGNMENTS_FIELD_NUMBER: _ClassVar[int]
    principal: _principal__client_pb2.PrincipalBasic
    role_assignments: _containers.RepeatedCompositeFieldContainer[_resource_role_assignments__client_pb2.ResourceAndRoleAssignmentsV2]
    def __init__(self, principal: _Optional[_Union[_principal__client_pb2.PrincipalBasic, _Mapping]] = ..., role_assignments: _Optional[_Iterable[_Union[_resource_role_assignments__client_pb2.ResourceAndRoleAssignmentsV2, _Mapping]]] = ...) -> None: ...

class GetAppPermissionsRequest(_message.Message):
    __slots__ = ["principal_type", "principal_id", "resource_type_permissions"]
    PRINCIPAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    principal_type: _principal__client_pb2.PrincipalType
    principal_id: str
    resource_type_permissions: _containers.RepeatedCompositeFieldContainer[ResourceTypePermissions]
    def __init__(self, principal_type: _Optional[_Union[_principal__client_pb2.PrincipalType, str]] = ..., principal_id: _Optional[str] = ..., resource_type_permissions: _Optional[_Iterable[_Union[ResourceTypePermissions, _Mapping]]] = ...) -> None: ...

class ResourceTypePermissions(_message.Message):
    __slots__ = ["resource_type", "actions"]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACTIONS_FIELD_NUMBER: _ClassVar[int]
    resource_type: _resource__client_pb2.ResourceType
    actions: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, resource_type: _Optional[_Union[_resource__client_pb2.ResourceType, str]] = ..., actions: _Optional[_Iterable[str]] = ...) -> None: ...

class GetAppPermissionsResponse(_message.Message):
    __slots__ = ["resource_type_permission_values"]
    RESOURCE_TYPE_PERMISSION_VALUES_FIELD_NUMBER: _ClassVar[int]
    resource_type_permission_values: _containers.RepeatedCompositeFieldContainer[ResourceTypePermissionValues]
    def __init__(self, resource_type_permission_values: _Optional[_Iterable[_Union[ResourceTypePermissionValues, _Mapping]]] = ...) -> None: ...

class ResourceTypePermissionValues(_message.Message):
    __slots__ = ["resource_type", "permission_values"]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_VALUES_FIELD_NUMBER: _ClassVar[int]
    resource_type: _resource__client_pb2.ResourceType
    permission_values: _containers.RepeatedCompositeFieldContainer[PermissionValue]
    def __init__(self, resource_type: _Optional[_Union[_resource__client_pb2.ResourceType, str]] = ..., permission_values: _Optional[_Iterable[_Union[PermissionValue, _Mapping]]] = ...) -> None: ...

class Permission(_message.Message):
    __slots__ = ["resource_type", "resource_id", "action"]
    RESOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    resource_type: _resource__client_pb2.ResourceType
    resource_id: str
    action: str
    def __init__(self, resource_type: _Optional[_Union[_resource__client_pb2.ResourceType, str]] = ..., resource_id: _Optional[str] = ..., action: _Optional[str] = ...) -> None: ...

class PermissionValue(_message.Message):
    __slots__ = ["action", "is_authorized"]
    ACTION_FIELD_NUMBER: _ClassVar[int]
    IS_AUTHORIZED_FIELD_NUMBER: _ClassVar[int]
    action: str
    is_authorized: bool
    def __init__(self, action: _Optional[str] = ..., is_authorized: bool = ...) -> None: ...

class GetWorkspacePermissionsRequest(_message.Message):
    __slots__ = ["principal_type", "principal_id", "workspace_id", "resource_type_permissions"]
    PRINCIPAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    PRINCIPAL_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ID_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_TYPE_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    principal_type: _principal__client_pb2.PrincipalType
    principal_id: str
    workspace_id: str
    resource_type_permissions: _containers.RepeatedCompositeFieldContainer[ResourceTypePermissions]
    def __init__(self, principal_type: _Optional[_Union[_principal__client_pb2.PrincipalType, str]] = ..., principal_id: _Optional[str] = ..., workspace_id: _Optional[str] = ..., resource_type_permissions: _Optional[_Iterable[_Union[ResourceTypePermissions, _Mapping]]] = ...) -> None: ...

class GetWorkspacePermissionsResponse(_message.Message):
    __slots__ = ["resource_type_permission_values"]
    RESOURCE_TYPE_PERMISSION_VALUES_FIELD_NUMBER: _ClassVar[int]
    resource_type_permission_values: _containers.RepeatedCompositeFieldContainer[ResourceTypePermissionValues]
    def __init__(self, resource_type_permission_values: _Optional[_Iterable[_Union[ResourceTypePermissionValues, _Mapping]]] = ...) -> None: ...
