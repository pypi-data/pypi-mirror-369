from tecton_proto.auth import service__client_pb2 as _service__client_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class IngestionServerConfigRequest(_message.Message):
    __slots__ = ["absolute_filepath", "offline_log_filepath"]
    ABSOLUTE_FILEPATH_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_LOG_FILEPATH_FIELD_NUMBER: _ClassVar[int]
    absolute_filepath: str
    offline_log_filepath: str
    def __init__(self, absolute_filepath: _Optional[str] = ..., offline_log_filepath: _Optional[str] = ...) -> None: ...

class IngestionServerConfigResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class IngestServerGroupConfigRequest(_message.Message):
    __slots__ = ["absolute_filepath", "workspace", "ingest_server_group_name"]
    ABSOLUTE_FILEPATH_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    INGEST_SERVER_GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    absolute_filepath: str
    workspace: str
    ingest_server_group_name: str
    def __init__(self, absolute_filepath: _Optional[str] = ..., workspace: _Optional[str] = ..., ingest_server_group_name: _Optional[str] = ...) -> None: ...

class IngestServerGroupConfigResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class InitializeStoreRequest(_message.Message):
    __slots__ = ["workspace", "feature_view_name"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    feature_view_name: str
    def __init__(self, workspace: _Optional[str] = ..., feature_view_name: _Optional[str] = ...) -> None: ...

class InitializeStoreResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
