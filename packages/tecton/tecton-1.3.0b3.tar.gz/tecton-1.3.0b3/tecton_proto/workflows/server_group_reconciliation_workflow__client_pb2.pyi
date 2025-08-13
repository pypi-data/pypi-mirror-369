from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServerGroupReconciliationWorkflowStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    SERVER_GROUP_RECONCILIATION_WORKFLOW_STATUS_UNSPECIFIED: _ClassVar[ServerGroupReconciliationWorkflowStatus]
    SERVER_GROUP_RECONCILIATION_WORKFLOW_STATUS_IN_PROGRESS: _ClassVar[ServerGroupReconciliationWorkflowStatus]
    SERVER_GROUP_RECONCILIATION_WORKFLOW_STATUS_SUCCESS: _ClassVar[ServerGroupReconciliationWorkflowStatus]
    SERVER_GROUP_RECONCILIATION_WORKFLOW_STATUS_FAILURE_OPERATION_IN_PROGRESS: _ClassVar[ServerGroupReconciliationWorkflowStatus]
    SERVER_GROUP_RECONCILIATION_WORKFLOW_STATUS_FAILURE_CORRUPTED_STATE: _ClassVar[ServerGroupReconciliationWorkflowStatus]
    SERVER_GROUP_RECONCILIATION_WORKFLOW_STATUS_FAILURE_ERROR: _ClassVar[ServerGroupReconciliationWorkflowStatus]
SERVER_GROUP_RECONCILIATION_WORKFLOW_STATUS_UNSPECIFIED: ServerGroupReconciliationWorkflowStatus
SERVER_GROUP_RECONCILIATION_WORKFLOW_STATUS_IN_PROGRESS: ServerGroupReconciliationWorkflowStatus
SERVER_GROUP_RECONCILIATION_WORKFLOW_STATUS_SUCCESS: ServerGroupReconciliationWorkflowStatus
SERVER_GROUP_RECONCILIATION_WORKFLOW_STATUS_FAILURE_OPERATION_IN_PROGRESS: ServerGroupReconciliationWorkflowStatus
SERVER_GROUP_RECONCILIATION_WORKFLOW_STATUS_FAILURE_CORRUPTED_STATE: ServerGroupReconciliationWorkflowStatus
SERVER_GROUP_RECONCILIATION_WORKFLOW_STATUS_FAILURE_ERROR: ServerGroupReconciliationWorkflowStatus

class ServerGroupReconciliationWorkflowState(_message.Message):
    __slots__ = ["status", "state_timestamp", "error_message"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATE_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: ServerGroupReconciliationWorkflowStatus
    state_timestamp: _timestamp_pb2.Timestamp
    error_message: str
    def __init__(self, status: _Optional[_Union[ServerGroupReconciliationWorkflowStatus, str]] = ..., state_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., error_message: _Optional[str] = ...) -> None: ...

class ServerGroupReconciliationWorkflow(_message.Message):
    __slots__ = ["server_group_state_id", "workspace", "state_transitions"]
    SERVER_GROUP_STATE_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    STATE_TRANSITIONS_FIELD_NUMBER: _ClassVar[int]
    server_group_state_id: _id__client_pb2.Id
    workspace: str
    state_transitions: _containers.RepeatedCompositeFieldContainer[ServerGroupReconciliationWorkflowState]
    def __init__(self, server_group_state_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., workspace: _Optional[str] = ..., state_transitions: _Optional[_Iterable[_Union[ServerGroupReconciliationWorkflowState, _Mapping]]] = ...) -> None: ...
