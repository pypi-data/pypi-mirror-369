from tecton_proto.workflows import state_machine_workflow__client_pb2 as _state_machine_workflow__client_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TestStateMachineWorkflowData(_message.Message):
    __slots__ = ["state", "max_iterations", "iteration_sleep_secs", "current_iteration", "succeed_after_attempt"]
    class TestStateMachineState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        UNKNOWN: _ClassVar[TestStateMachineWorkflowData.TestStateMachineState]
        START: _ClassVar[TestStateMachineWorkflowData.TestStateMachineState]
        RUNNING_EVEN: _ClassVar[TestStateMachineWorkflowData.TestStateMachineState]
        RUNNING_ODD: _ClassVar[TestStateMachineWorkflowData.TestStateMachineState]
        SUCCESS: _ClassVar[TestStateMachineWorkflowData.TestStateMachineState]
        FAILURE: _ClassVar[TestStateMachineWorkflowData.TestStateMachineState]
        CANCELLING: _ClassVar[TestStateMachineWorkflowData.TestStateMachineState]
        CANCELLED: _ClassVar[TestStateMachineWorkflowData.TestStateMachineState]
    UNKNOWN: TestStateMachineWorkflowData.TestStateMachineState
    START: TestStateMachineWorkflowData.TestStateMachineState
    RUNNING_EVEN: TestStateMachineWorkflowData.TestStateMachineState
    RUNNING_ODD: TestStateMachineWorkflowData.TestStateMachineState
    SUCCESS: TestStateMachineWorkflowData.TestStateMachineState
    FAILURE: TestStateMachineWorkflowData.TestStateMachineState
    CANCELLING: TestStateMachineWorkflowData.TestStateMachineState
    CANCELLED: TestStateMachineWorkflowData.TestStateMachineState
    STATE_FIELD_NUMBER: _ClassVar[int]
    MAX_ITERATIONS_FIELD_NUMBER: _ClassVar[int]
    ITERATION_SLEEP_SECS_FIELD_NUMBER: _ClassVar[int]
    CURRENT_ITERATION_FIELD_NUMBER: _ClassVar[int]
    SUCCEED_AFTER_ATTEMPT_FIELD_NUMBER: _ClassVar[int]
    state: TestStateMachineWorkflowData.TestStateMachineState
    max_iterations: int
    iteration_sleep_secs: int
    current_iteration: int
    succeed_after_attempt: int
    def __init__(self, state: _Optional[_Union[TestStateMachineWorkflowData.TestStateMachineState, str]] = ..., max_iterations: _Optional[int] = ..., iteration_sleep_secs: _Optional[int] = ..., current_iteration: _Optional[int] = ..., succeed_after_attempt: _Optional[int] = ...) -> None: ...
