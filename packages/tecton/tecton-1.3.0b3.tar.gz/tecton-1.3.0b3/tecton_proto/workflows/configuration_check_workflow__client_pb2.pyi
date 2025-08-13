from tecton_proto.workflows import state_machine_workflow__client_pb2 as _state_machine_workflow__client_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ConfigurationCheckWorkflowData(_message.Message):
    __slots__ = ["state"]
    class ConfigurationCheckState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        UNKNOWN: _ClassVar[ConfigurationCheckWorkflowData.ConfigurationCheckState]
        START: _ClassVar[ConfigurationCheckWorkflowData.ConfigurationCheckState]
        SUCCESS: _ClassVar[ConfigurationCheckWorkflowData.ConfigurationCheckState]
        FAILURE: _ClassVar[ConfigurationCheckWorkflowData.ConfigurationCheckState]
        CANCELLED: _ClassVar[ConfigurationCheckWorkflowData.ConfigurationCheckState]
    UNKNOWN: ConfigurationCheckWorkflowData.ConfigurationCheckState
    START: ConfigurationCheckWorkflowData.ConfigurationCheckState
    SUCCESS: ConfigurationCheckWorkflowData.ConfigurationCheckState
    FAILURE: ConfigurationCheckWorkflowData.ConfigurationCheckState
    CANCELLED: ConfigurationCheckWorkflowData.ConfigurationCheckState
    STATE_FIELD_NUMBER: _ClassVar[int]
    state: ConfigurationCheckWorkflowData.ConfigurationCheckState
    def __init__(self, state: _Optional[_Union[ConfigurationCheckWorkflowData.ConfigurationCheckState, str]] = ...) -> None: ...
