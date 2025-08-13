from google.protobuf import duration_pb2 as _duration_pb2
from tecton_proto.amplitude import client_logging__client_pb2 as _client_logging__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AmplitudeEvent(_message.Message):
    __slots__ = ["user_id", "device_id", "event_type", "platform", "session_id", "timestamp", "os_name", "os_version", "event_properties"]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    DEVICE_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    PLATFORM_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    OS_NAME_FIELD_NUMBER: _ClassVar[int]
    OS_VERSION_FIELD_NUMBER: _ClassVar[int]
    EVENT_PROPERTIES_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    device_id: str
    event_type: str
    platform: str
    session_id: int
    timestamp: int
    os_name: str
    os_version: str
    event_properties: AmplitudeEventProperties
    def __init__(self, user_id: _Optional[str] = ..., device_id: _Optional[str] = ..., event_type: _Optional[str] = ..., platform: _Optional[str] = ..., session_id: _Optional[int] = ..., timestamp: _Optional[int] = ..., os_name: _Optional[str] = ..., os_version: _Optional[str] = ..., event_properties: _Optional[_Union[AmplitudeEventProperties, _Mapping]] = ...) -> None: ...

class AmplitudeEventProperties(_message.Message):
    __slots__ = ["cluster_name", "workspace", "sdk_version", "python_version", "execution_time", "num_total_fcos", "num_fcos_changed", "num_v3_fcos", "num_v5_fcos", "suppress_recreates", "json_out", "success", "error_message", "num_warnings", "params", "sdk_method_invocation", "status", "caller_identity"]
    class ParamsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    SDK_VERSION_FIELD_NUMBER: _ClassVar[int]
    PYTHON_VERSION_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_TIME_FIELD_NUMBER: _ClassVar[int]
    NUM_TOTAL_FCOS_FIELD_NUMBER: _ClassVar[int]
    NUM_FCOS_CHANGED_FIELD_NUMBER: _ClassVar[int]
    NUM_V3_FCOS_FIELD_NUMBER: _ClassVar[int]
    NUM_V5_FCOS_FIELD_NUMBER: _ClassVar[int]
    SUPPRESS_RECREATES_FIELD_NUMBER: _ClassVar[int]
    JSON_OUT_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    NUM_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    PARAMS_FIELD_NUMBER: _ClassVar[int]
    SDK_METHOD_INVOCATION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CALLER_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    cluster_name: str
    workspace: str
    sdk_version: str
    python_version: str
    execution_time: _duration_pb2.Duration
    num_total_fcos: int
    num_fcos_changed: int
    num_v3_fcos: int
    num_v5_fcos: int
    suppress_recreates: bool
    json_out: bool
    success: bool
    error_message: str
    num_warnings: int
    params: _containers.ScalarMap[str, str]
    sdk_method_invocation: _client_logging__client_pb2.SDKMethodInvocation
    status: str
    caller_identity: CallerIdentity
    def __init__(self, cluster_name: _Optional[str] = ..., workspace: _Optional[str] = ..., sdk_version: _Optional[str] = ..., python_version: _Optional[str] = ..., execution_time: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., num_total_fcos: _Optional[int] = ..., num_fcos_changed: _Optional[int] = ..., num_v3_fcos: _Optional[int] = ..., num_v5_fcos: _Optional[int] = ..., suppress_recreates: bool = ..., json_out: bool = ..., success: bool = ..., error_message: _Optional[str] = ..., num_warnings: _Optional[int] = ..., params: _Optional[_Mapping[str, str]] = ..., sdk_method_invocation: _Optional[_Union[_client_logging__client_pb2.SDKMethodInvocation, _Mapping]] = ..., status: _Optional[str] = ..., caller_identity: _Optional[_Union[CallerIdentity, _Mapping]] = ...) -> None: ...

class CallerIdentity(_message.Message):
    __slots__ = ["id", "name", "identity_type"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    IDENTITY_TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    identity_type: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., identity_type: _Optional[str] = ...) -> None: ...

class UploadRequest(_message.Message):
    __slots__ = ["api_key", "events"]
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    EVENTS_FIELD_NUMBER: _ClassVar[int]
    api_key: str
    events: _containers.RepeatedCompositeFieldContainer[AmplitudeEvent]
    def __init__(self, api_key: _Optional[str] = ..., events: _Optional[_Iterable[_Union[AmplitudeEvent, _Mapping]]] = ...) -> None: ...

class UploadResponse(_message.Message):
    __slots__ = ["code", "events_ingested", "payload_size_bytes", "server_upload_time", "error", "missing_field"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    EVENTS_INGESTED_FIELD_NUMBER: _ClassVar[int]
    PAYLOAD_SIZE_BYTES_FIELD_NUMBER: _ClassVar[int]
    SERVER_UPLOAD_TIME_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    MISSING_FIELD_FIELD_NUMBER: _ClassVar[int]
    code: int
    events_ingested: int
    payload_size_bytes: int
    server_upload_time: int
    error: str
    missing_field: str
    def __init__(self, code: _Optional[int] = ..., events_ingested: _Optional[int] = ..., payload_size_bytes: _Optional[int] = ..., server_upload_time: _Optional[int] = ..., error: _Optional[str] = ..., missing_field: _Optional[str] = ...) -> None: ...
