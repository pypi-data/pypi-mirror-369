from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor
STATE_FIELD_FIELD_NUMBER: _ClassVar[int]
state_field: _descriptor.FieldDescriptor
LEGACY_STATE_HISTORY_FIELD_FIELD_NUMBER: _ClassVar[int]
legacy_state_history_field: _descriptor.FieldDescriptor
TERMINAL_FIELD_NUMBER: _ClassVar[int]
terminal: _descriptor.FieldDescriptor

class TerminalStateOptions(_message.Message):
    __slots__ = ["termination_code", "retry_policy"]
    class WorkflowTerminationCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        OK: _ClassVar[TerminalStateOptions.WorkflowTerminationCode]
        CANCELLED: _ClassVar[TerminalStateOptions.WorkflowTerminationCode]
        UNKNOWN_ERROR: _ClassVar[TerminalStateOptions.WorkflowTerminationCode]
    OK: TerminalStateOptions.WorkflowTerminationCode
    CANCELLED: TerminalStateOptions.WorkflowTerminationCode
    UNKNOWN_ERROR: TerminalStateOptions.WorkflowTerminationCode
    class RetryPolicy(_message.Message):
        __slots__ = ["enabled"]
        ENABLED_FIELD_NUMBER: _ClassVar[int]
        enabled: bool
        def __init__(self, enabled: bool = ...) -> None: ...
    TERMINATION_CODE_FIELD_NUMBER: _ClassVar[int]
    RETRY_POLICY_FIELD_NUMBER: _ClassVar[int]
    termination_code: TerminalStateOptions.WorkflowTerminationCode
    retry_policy: TerminalStateOptions.RetryPolicy
    def __init__(self, termination_code: _Optional[_Union[TerminalStateOptions.WorkflowTerminationCode, str]] = ..., retry_policy: _Optional[_Union[TerminalStateOptions.RetryPolicy, _Mapping]] = ...) -> None: ...
