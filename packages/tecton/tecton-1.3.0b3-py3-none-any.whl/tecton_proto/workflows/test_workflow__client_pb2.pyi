from tecton_proto.workflows import state_machine_workflow__client_pb2 as _state_machine_workflow__client_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TestWorkflowState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNKNOWN: _ClassVar[TestWorkflowState]
    RUNNING: _ClassVar[TestWorkflowState]
    SUCCESS: _ClassVar[TestWorkflowState]
    CANCELED: _ClassVar[TestWorkflowState]
UNKNOWN: TestWorkflowState
RUNNING: TestWorkflowState
SUCCESS: TestWorkflowState
CANCELED: TestWorkflowState

class TestWorkflow(_message.Message):
    __slots__ = ["max_iterations", "iteration_sleep_secs", "current_iteration", "state", "num_attempts"]
    MAX_ITERATIONS_FIELD_NUMBER: _ClassVar[int]
    ITERATION_SLEEP_SECS_FIELD_NUMBER: _ClassVar[int]
    CURRENT_ITERATION_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    NUM_ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    max_iterations: int
    iteration_sleep_secs: int
    current_iteration: int
    state: TestWorkflowState
    num_attempts: int
    def __init__(self, max_iterations: _Optional[int] = ..., iteration_sleep_secs: _Optional[int] = ..., current_iteration: _Optional[int] = ..., state: _Optional[_Union[TestWorkflowState, str]] = ..., num_attempts: _Optional[int] = ...) -> None: ...
