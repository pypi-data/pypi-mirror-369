from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class GroupPermissionsObject(_message.Message):
    __slots__ = ["group_name", "permission_level", "user_name", "service_principal_name"]
    GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_LEVEL_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    SERVICE_PRINCIPAL_NAME_FIELD_NUMBER: _ClassVar[int]
    group_name: str
    permission_level: str
    user_name: str
    service_principal_name: str
    def __init__(self, group_name: _Optional[str] = ..., permission_level: _Optional[str] = ..., user_name: _Optional[str] = ..., service_principal_name: _Optional[str] = ...) -> None: ...

class PermissionObject(_message.Message):
    __slots__ = ["permission_level", "inherited", "inherited_from_object"]
    PERMISSION_LEVEL_FIELD_NUMBER: _ClassVar[int]
    INHERITED_FIELD_NUMBER: _ClassVar[int]
    INHERITED_FROM_OBJECT_FIELD_NUMBER: _ClassVar[int]
    permission_level: str
    inherited: bool
    inherited_from_object: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, permission_level: _Optional[str] = ..., inherited: bool = ..., inherited_from_object: _Optional[_Iterable[str]] = ...) -> None: ...

class AccessControlListResponse(_message.Message):
    __slots__ = ["user_name", "group_name", "service_principal_name", "display_name", "all_permissions"]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    SERVICE_PRINCIPAL_NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    ALL_PERMISSIONS_FIELD_NUMBER: _ClassVar[int]
    user_name: str
    group_name: str
    service_principal_name: str
    display_name: str
    all_permissions: _containers.RepeatedCompositeFieldContainer[PermissionObject]
    def __init__(self, user_name: _Optional[str] = ..., group_name: _Optional[str] = ..., service_principal_name: _Optional[str] = ..., display_name: _Optional[str] = ..., all_permissions: _Optional[_Iterable[_Union[PermissionObject, _Mapping]]] = ...) -> None: ...

class PermissionsRequest(_message.Message):
    __slots__ = ["access_control_list"]
    ACCESS_CONTROL_LIST_FIELD_NUMBER: _ClassVar[int]
    access_control_list: _containers.RepeatedCompositeFieldContainer[GroupPermissionsObject]
    def __init__(self, access_control_list: _Optional[_Iterable[_Union[GroupPermissionsObject, _Mapping]]] = ...) -> None: ...

class PermissionsResponse(_message.Message):
    __slots__ = ["object_id", "object_type", "access_control_list"]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    ACCESS_CONTROL_LIST_FIELD_NUMBER: _ClassVar[int]
    object_id: str
    object_type: str
    access_control_list: _containers.RepeatedCompositeFieldContainer[AccessControlListResponse]
    def __init__(self, object_id: _Optional[str] = ..., object_type: _Optional[str] = ..., access_control_list: _Optional[_Iterable[_Union[AccessControlListResponse, _Mapping]]] = ...) -> None: ...
