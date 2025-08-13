from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import compute_identity__client_pb2 as _compute_identity__client_pb2
from tecton_proto.spark_common import clusters__client_pb2 as _clusters__client_pb2
from tecton_proto.spark_common import libraries__client_pb2 as _libraries__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class RunStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    RUN_STATUS_UNKNOWN: _ClassVar[RunStatus]
    RUN_STATUS_PENDING: _ClassVar[RunStatus]
    RUN_STATUS_RUNNING: _ClassVar[RunStatus]
    RUN_STATUS_SUCCESS: _ClassVar[RunStatus]
    RUN_STATUS_ERROR: _ClassVar[RunStatus]
    RUN_STATUS_TERMINATING: _ClassVar[RunStatus]
    RUN_STATUS_CANCELED: _ClassVar[RunStatus]
    RUN_STATUS_SUBMISSION_ERROR: _ClassVar[RunStatus]

class RunTerminationReason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNKNOWN_TERMINATION_REASON: _ClassVar[RunTerminationReason]
    JOB_FINISHED: _ClassVar[RunTerminationReason]
    MANUAL_CANCELATION: _ClassVar[RunTerminationReason]
    INSTANCE_ALLOCATION_FAILURE: _ClassVar[RunTerminationReason]
    NON_CLOUD_FAILURE: _ClassVar[RunTerminationReason]
    SUBMISSION_ERROR: _ClassVar[RunTerminationReason]
RUN_STATUS_UNKNOWN: RunStatus
RUN_STATUS_PENDING: RunStatus
RUN_STATUS_RUNNING: RunStatus
RUN_STATUS_SUCCESS: RunStatus
RUN_STATUS_ERROR: RunStatus
RUN_STATUS_TERMINATING: RunStatus
RUN_STATUS_CANCELED: RunStatus
RUN_STATUS_SUBMISSION_ERROR: RunStatus
UNKNOWN_TERMINATION_REASON: RunTerminationReason
JOB_FINISHED: RunTerminationReason
MANUAL_CANCELATION: RunTerminationReason
INSTANCE_ALLOCATION_FAILURE: RunTerminationReason
NON_CLOUD_FAILURE: RunTerminationReason
SUBMISSION_ERROR: RunTerminationReason

class PythonMaterializationTask(_message.Message):
    __slots__ = ["materialization_path_uri", "base_parameters", "taskType"]
    class TaskType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        STREAMING: _ClassVar[PythonMaterializationTask.TaskType]
        BATCH: _ClassVar[PythonMaterializationTask.TaskType]
        INGEST: _ClassVar[PythonMaterializationTask.TaskType]
        DELETION: _ClassVar[PythonMaterializationTask.TaskType]
        DELTA_MAINTENANCE: _ClassVar[PythonMaterializationTask.TaskType]
        ICEBERG_MAINTENANCE: _ClassVar[PythonMaterializationTask.TaskType]
        FEATURE_EXPORT: _ClassVar[PythonMaterializationTask.TaskType]
        DATASET_GENERATION: _ClassVar[PythonMaterializationTask.TaskType]
        PLAN_INTEGRATION_TEST_BATCH: _ClassVar[PythonMaterializationTask.TaskType]
        PLAN_INTEGRATION_TEST_STREAM: _ClassVar[PythonMaterializationTask.TaskType]
    STREAMING: PythonMaterializationTask.TaskType
    BATCH: PythonMaterializationTask.TaskType
    INGEST: PythonMaterializationTask.TaskType
    DELETION: PythonMaterializationTask.TaskType
    DELTA_MAINTENANCE: PythonMaterializationTask.TaskType
    ICEBERG_MAINTENANCE: PythonMaterializationTask.TaskType
    FEATURE_EXPORT: PythonMaterializationTask.TaskType
    DATASET_GENERATION: PythonMaterializationTask.TaskType
    PLAN_INTEGRATION_TEST_BATCH: PythonMaterializationTask.TaskType
    PLAN_INTEGRATION_TEST_STREAM: PythonMaterializationTask.TaskType
    class BaseParametersEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    MATERIALIZATION_PATH_URI_FIELD_NUMBER: _ClassVar[int]
    BASE_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    TASKTYPE_FIELD_NUMBER: _ClassVar[int]
    materialization_path_uri: str
    base_parameters: _containers.ScalarMap[str, str]
    taskType: PythonMaterializationTask.TaskType
    def __init__(self, materialization_path_uri: _Optional[str] = ..., base_parameters: _Optional[_Mapping[str, str]] = ..., taskType: _Optional[_Union[PythonMaterializationTask.TaskType, str]] = ...) -> None: ...

class StartJobRequest(_message.Message):
    __slots__ = ["new_cluster", "existing_cluster", "materialization_task", "run_name", "libraries", "timeout_seconds", "is_notebook", "use_stepped_materialization", "databricks_jobs_api_version", "compute_identity"]
    NEW_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    EXISTING_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_TASK_FIELD_NUMBER: _ClassVar[int]
    RUN_NAME_FIELD_NUMBER: _ClassVar[int]
    LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    IS_NOTEBOOK_FIELD_NUMBER: _ClassVar[int]
    USE_STEPPED_MATERIALIZATION_FIELD_NUMBER: _ClassVar[int]
    DATABRICKS_JOBS_API_VERSION_FIELD_NUMBER: _ClassVar[int]
    COMPUTE_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    new_cluster: _clusters__client_pb2.NewCluster
    existing_cluster: _clusters__client_pb2.ExistingCluster
    materialization_task: PythonMaterializationTask
    run_name: str
    libraries: _containers.RepeatedCompositeFieldContainer[_libraries__client_pb2.Library]
    timeout_seconds: int
    is_notebook: bool
    use_stepped_materialization: bool
    databricks_jobs_api_version: str
    compute_identity: _compute_identity__client_pb2.ComputeIdentity
    def __init__(self, new_cluster: _Optional[_Union[_clusters__client_pb2.NewCluster, _Mapping]] = ..., existing_cluster: _Optional[_Union[_clusters__client_pb2.ExistingCluster, _Mapping]] = ..., materialization_task: _Optional[_Union[PythonMaterializationTask, _Mapping]] = ..., run_name: _Optional[str] = ..., libraries: _Optional[_Iterable[_Union[_libraries__client_pb2.Library, _Mapping]]] = ..., timeout_seconds: _Optional[int] = ..., is_notebook: bool = ..., use_stepped_materialization: bool = ..., databricks_jobs_api_version: _Optional[str] = ..., compute_identity: _Optional[_Union[_compute_identity__client_pb2.ComputeIdentity, _Mapping]] = ...) -> None: ...

class StartJobResponse(_message.Message):
    __slots__ = ["run_id"]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    def __init__(self, run_id: _Optional[str] = ...) -> None: ...

class GetJobRequest(_message.Message):
    __slots__ = ["run_id"]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    def __init__(self, run_id: _Optional[str] = ...) -> None: ...

class GetJobResponse(_message.Message):
    __slots__ = ["run_id", "job_id", "run_page_url", "spark_cluster_id", "details", "additional_metadata"]
    class AdditionalMetadataEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    SPARK_CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    job_id: str
    run_page_url: str
    spark_cluster_id: str
    details: RunDetails
    additional_metadata: _containers.ScalarMap[str, str]
    def __init__(self, run_id: _Optional[str] = ..., job_id: _Optional[str] = ..., run_page_url: _Optional[str] = ..., spark_cluster_id: _Optional[str] = ..., details: _Optional[_Union[RunDetails, _Mapping]] = ..., additional_metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class RunDetails(_message.Message):
    __slots__ = ["run_status", "termination_reason", "state_message", "vendor_termination_reason", "start_time", "end_time"]
    RUN_STATUS_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_REASON_FIELD_NUMBER: _ClassVar[int]
    STATE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    VENDOR_TERMINATION_REASON_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    run_status: RunStatus
    termination_reason: RunTerminationReason
    state_message: str
    vendor_termination_reason: str
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    def __init__(self, run_status: _Optional[_Union[RunStatus, str]] = ..., termination_reason: _Optional[_Union[RunTerminationReason, str]] = ..., state_message: _Optional[str] = ..., vendor_termination_reason: _Optional[str] = ..., start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class StopJobRequest(_message.Message):
    __slots__ = ["run_id"]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    def __init__(self, run_id: _Optional[str] = ...) -> None: ...

class ListJobRequest(_message.Message):
    __slots__ = ["offset", "marker"]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    MARKER_FIELD_NUMBER: _ClassVar[int]
    offset: int
    marker: str
    def __init__(self, offset: _Optional[int] = ..., marker: _Optional[str] = ...) -> None: ...

class RunSummary(_message.Message):
    __slots__ = ["run_id", "run_state", "resource_locator", "additional_metadata"]
    class AdditionalMetadataEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_STATE_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_LOCATOR_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_METADATA_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    run_state: str
    resource_locator: str
    additional_metadata: _containers.ScalarMap[str, str]
    def __init__(self, run_id: _Optional[str] = ..., run_state: _Optional[str] = ..., resource_locator: _Optional[str] = ..., additional_metadata: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ListJobResponse(_message.Message):
    __slots__ = ["runs", "has_more", "marker"]
    RUNS_FIELD_NUMBER: _ClassVar[int]
    HAS_MORE_FIELD_NUMBER: _ClassVar[int]
    MARKER_FIELD_NUMBER: _ClassVar[int]
    runs: _containers.RepeatedCompositeFieldContainer[RunSummary]
    has_more: bool
    marker: str
    def __init__(self, runs: _Optional[_Iterable[_Union[RunSummary, _Mapping]]] = ..., has_more: bool = ..., marker: _Optional[str] = ...) -> None: ...
