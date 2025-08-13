from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import server_group_type__client_pb2 as _server_group_type__client_pb2
from tecton_proto.workflows import state_machine_workflow__client_pb2 as _state_machine_workflow__client_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServerGroupStateMachineWorkflowData(_message.Message):
    __slots__ = ["state", "consecutive_failed_updates", "server_group_state_id", "workspace", "server_group_type", "error_message"]
    class ServerGroupStateMachineWorkflowState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        UNSPECIFIED: _ClassVar[ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState]
        PENDING: _ClassVar[ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState]
        RUNNING: _ClassVar[ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState]
        CANCELLING: _ClassVar[ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState]
        CANCELLED_DELETED: _ClassVar[ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState]
        CANCELLED: _ClassVar[ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState]
        PERMANENTLY_FAILED: _ClassVar[ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState]
    UNSPECIFIED: ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState
    PENDING: ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState
    RUNNING: ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState
    CANCELLING: ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState
    CANCELLED_DELETED: ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState
    CANCELLED: ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState
    PERMANENTLY_FAILED: ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState
    STATE_FIELD_NUMBER: _ClassVar[int]
    CONSECUTIVE_FAILED_UPDATES_FIELD_NUMBER: _ClassVar[int]
    SERVER_GROUP_STATE_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    SERVER_GROUP_TYPE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    state: ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState
    consecutive_failed_updates: int
    server_group_state_id: _id__client_pb2.Id
    workspace: str
    server_group_type: _server_group_type__client_pb2.ServerGroupType
    error_message: str
    def __init__(self, state: _Optional[_Union[ServerGroupStateMachineWorkflowData.ServerGroupStateMachineWorkflowState, str]] = ..., consecutive_failed_updates: _Optional[int] = ..., server_group_state_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., workspace: _Optional[str] = ..., server_group_type: _Optional[_Union[_server_group_type__client_pb2.ServerGroupType, str]] = ..., error_message: _Optional[str] = ...) -> None: ...
