from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.workflows import state_machine_workflow__client_pb2 as _state_machine_workflow__client_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class EMRValidationClusterWorkflowState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    EMR_VALIDATION_CLUSTER_WORKFLOW_STATE_UNKNOWN: _ClassVar[EMRValidationClusterWorkflowState]
    EMR_VALIDATION_CLUSTER_WORKFLOW_STATE_NO_ACTIVE_CLUSTERS: _ClassVar[EMRValidationClusterWorkflowState]
    EMR_VALIDATION_CLUSTER_WORKFLOW_STATE_RUNNING: _ClassVar[EMRValidationClusterWorkflowState]
    EMR_VALIDATION_CLUSTER_WORKFLOW_STATE_UPGRADING: _ClassVar[EMRValidationClusterWorkflowState]
EMR_VALIDATION_CLUSTER_WORKFLOW_STATE_UNKNOWN: EMRValidationClusterWorkflowState
EMR_VALIDATION_CLUSTER_WORKFLOW_STATE_NO_ACTIVE_CLUSTERS: EMRValidationClusterWorkflowState
EMR_VALIDATION_CLUSTER_WORKFLOW_STATE_RUNNING: EMRValidationClusterWorkflowState
EMR_VALIDATION_CLUSTER_WORKFLOW_STATE_UPGRADING: EMRValidationClusterWorkflowState

class EMRValidationClusterWorkflowProto(_message.Message):
    __slots__ = ["state", "canonical_cluster", "state_reported_at", "next_cluster"]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CANONICAL_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    STATE_REPORTED_AT_FIELD_NUMBER: _ClassVar[int]
    NEXT_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    state: EMRValidationClusterWorkflowState
    canonical_cluster: ClusterMetadata
    state_reported_at: _timestamp_pb2.Timestamp
    next_cluster: ClusterMetadata
    def __init__(self, state: _Optional[_Union[EMRValidationClusterWorkflowState, str]] = ..., canonical_cluster: _Optional[_Union[ClusterMetadata, _Mapping]] = ..., state_reported_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., next_cluster: _Optional[_Union[ClusterMetadata, _Mapping]] = ...) -> None: ...

class ClusterMetadata(_message.Message):
    __slots__ = ["cluster_id", "emr_release_label", "error_message", "launched_at"]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    EMR_RELEASE_LABEL_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    LAUNCHED_AT_FIELD_NUMBER: _ClassVar[int]
    cluster_id: str
    emr_release_label: str
    error_message: str
    launched_at: _timestamp_pb2.Timestamp
    def __init__(self, cluster_id: _Optional[str] = ..., emr_release_label: _Optional[str] = ..., error_message: _Optional[str] = ..., launched_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
