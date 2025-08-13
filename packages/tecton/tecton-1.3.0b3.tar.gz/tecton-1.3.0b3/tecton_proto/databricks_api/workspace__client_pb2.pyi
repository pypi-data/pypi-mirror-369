from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ListWorkspaceRequest(_message.Message):
    __slots__ = ["path"]
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class ListWorkspaceResponse(_message.Message):
    __slots__ = ["objects"]
    OBJECTS_FIELD_NUMBER: _ClassVar[int]
    objects: _containers.RepeatedCompositeFieldContainer[ObjectInfo]
    def __init__(self, objects: _Optional[_Iterable[_Union[ObjectInfo, _Mapping]]] = ...) -> None: ...

class ObjectInfo(_message.Message):
    __slots__ = ["object_type", "object_id", "path", "language"]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    object_id: int
    path: str
    language: str
    def __init__(self, object_type: _Optional[str] = ..., object_id: _Optional[int] = ..., path: _Optional[str] = ..., language: _Optional[str] = ...) -> None: ...

class CreateWorkspaceDirectoryRequest(_message.Message):
    __slots__ = ["path"]
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class GetWorkspaceObjectStatusRequest(_message.Message):
    __slots__ = ["path"]
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class GetWorkspaceObjectStatusResponse(_message.Message):
    __slots__ = ["object_type", "path", "language", "created_at", "modified_at", "object_id", "size"]
    OBJECT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_AT_FIELD_NUMBER: _ClassVar[int]
    OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    object_type: str
    path: str
    language: str
    created_at: int
    modified_at: int
    object_id: int
    size: int
    def __init__(self, object_type: _Optional[str] = ..., path: _Optional[str] = ..., language: _Optional[str] = ..., created_at: _Optional[int] = ..., modified_at: _Optional[int] = ..., object_id: _Optional[int] = ..., size: _Optional[int] = ...) -> None: ...
