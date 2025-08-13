from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.materialization import job_metadata__client_pb2 as _job_metadata__client_pb2
from tecton_proto.materialization import materialization_task__client_pb2 as _materialization_task__client_pb2
from tecton_proto.materialization import spark_cluster__client_pb2 as _spark_cluster__client_pb2
from tecton_proto.spark_api import jobs__client_pb2 as _jobs__client_pb2
from tecton_proto.spark_common import clusters__client_pb2 as _clusters__client_pb2
from tecton_proto.workflows import state_machine_workflow__client_pb2 as _state_machine_workflow__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SparkExecutionWorkflowState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    SPARK_EXECUTION_WORKFLOW_STATE_UNKNOWN: _ClassVar[SparkExecutionWorkflowState]
    SPARK_EXECUTION_WORKFLOW_STATE_RUNNING: _ClassVar[SparkExecutionWorkflowState]
    SPARK_EXECUTION_WORKFLOW_STATE_SUCCESS: _ClassVar[SparkExecutionWorkflowState]
    SPARK_EXECUTION_WORKFLOW_STATE_FAILURE: _ClassVar[SparkExecutionWorkflowState]
    SPARK_EXECUTION_WORKFLOW_STATE_CANCELLATION_REQUESTED: _ClassVar[SparkExecutionWorkflowState]
    SPARK_EXECUTION_WORKFLOW_STATE_CANCELLED: _ClassVar[SparkExecutionWorkflowState]
    SPARK_EXECUTION_WORKFLOW_STATE_POST_JOB_HOOKS_SUBMITTED: _ClassVar[SparkExecutionWorkflowState]
    SPARK_EXECUTION_WORKFLOW_STATE_CLEANING_UP: _ClassVar[SparkExecutionWorkflowState]

class SparkExecutionAttemptState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    SPARK_EXECUTION_ATTEMPT_STATE_UNKNOWN: _ClassVar[SparkExecutionAttemptState]
    SPARK_EXECUTION_ATTEMPT_STATE_PENDING: _ClassVar[SparkExecutionAttemptState]
    SPARK_EXECUTION_ATTEMPT_STATE_RUNNING: _ClassVar[SparkExecutionAttemptState]
    SPARK_EXECUTION_ATTEMPT_STATE_SUCCESS: _ClassVar[SparkExecutionAttemptState]
    SPARK_EXECUTION_ATTEMPT_STATE_ERROR: _ClassVar[SparkExecutionAttemptState]
    SPARK_EXECUTION_ATTEMPT_STATE_CANCELLED: _ClassVar[SparkExecutionAttemptState]
SPARK_EXECUTION_WORKFLOW_STATE_UNKNOWN: SparkExecutionWorkflowState
SPARK_EXECUTION_WORKFLOW_STATE_RUNNING: SparkExecutionWorkflowState
SPARK_EXECUTION_WORKFLOW_STATE_SUCCESS: SparkExecutionWorkflowState
SPARK_EXECUTION_WORKFLOW_STATE_FAILURE: SparkExecutionWorkflowState
SPARK_EXECUTION_WORKFLOW_STATE_CANCELLATION_REQUESTED: SparkExecutionWorkflowState
SPARK_EXECUTION_WORKFLOW_STATE_CANCELLED: SparkExecutionWorkflowState
SPARK_EXECUTION_WORKFLOW_STATE_POST_JOB_HOOKS_SUBMITTED: SparkExecutionWorkflowState
SPARK_EXECUTION_WORKFLOW_STATE_CLEANING_UP: SparkExecutionWorkflowState
SPARK_EXECUTION_ATTEMPT_STATE_UNKNOWN: SparkExecutionAttemptState
SPARK_EXECUTION_ATTEMPT_STATE_PENDING: SparkExecutionAttemptState
SPARK_EXECUTION_ATTEMPT_STATE_RUNNING: SparkExecutionAttemptState
SPARK_EXECUTION_ATTEMPT_STATE_SUCCESS: SparkExecutionAttemptState
SPARK_EXECUTION_ATTEMPT_STATE_ERROR: SparkExecutionAttemptState
SPARK_EXECUTION_ATTEMPT_STATE_CANCELLED: SparkExecutionAttemptState

class SparkExecutionWorkflow(_message.Message):
    __slots__ = ["state_transitions", "spark_job_config", "attempt", "is_migrated", "last_job_poll", "uses_job_metadata_table", "uses_new_consumption_metrics", "validation_workflow_id", "import_table_info"]
    STATE_TRANSITIONS_FIELD_NUMBER: _ClassVar[int]
    SPARK_JOB_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ATTEMPT_FIELD_NUMBER: _ClassVar[int]
    IS_MIGRATED_FIELD_NUMBER: _ClassVar[int]
    LAST_JOB_POLL_FIELD_NUMBER: _ClassVar[int]
    USES_JOB_METADATA_TABLE_FIELD_NUMBER: _ClassVar[int]
    USES_NEW_CONSUMPTION_METRICS_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    IMPORT_TABLE_INFO_FIELD_NUMBER: _ClassVar[int]
    state_transitions: _containers.RepeatedCompositeFieldContainer[SparkExecutionWorkflowStateTransition]
    spark_job_config: SparkJobConfig
    attempt: SparkExecutionAttempt
    is_migrated: bool
    last_job_poll: _timestamp_pb2.Timestamp
    uses_job_metadata_table: bool
    uses_new_consumption_metrics: bool
    validation_workflow_id: _id__client_pb2.Id
    import_table_info: ImportTableInfo
    def __init__(self, state_transitions: _Optional[_Iterable[_Union[SparkExecutionWorkflowStateTransition, _Mapping]]] = ..., spark_job_config: _Optional[_Union[SparkJobConfig, _Mapping]] = ..., attempt: _Optional[_Union[SparkExecutionAttempt, _Mapping]] = ..., is_migrated: bool = ..., last_job_poll: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., uses_job_metadata_table: bool = ..., uses_new_consumption_metrics: bool = ..., validation_workflow_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., import_table_info: _Optional[_Union[ImportTableInfo, _Mapping]] = ...) -> None: ...

class ImportTableInfo(_message.Message):
    __slots__ = ["enabled", "import_path", "import_workflow_id"]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    IMPORT_PATH_FIELD_NUMBER: _ClassVar[int]
    IMPORT_WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    import_path: str
    import_workflow_id: _id__client_pb2.Id
    def __init__(self, enabled: bool = ..., import_path: _Optional[str] = ..., import_workflow_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ...) -> None: ...

class SparkExecutionWorkflowStateTransition(_message.Message):
    __slots__ = ["workflow_state", "timestamp"]
    WORKFLOW_STATE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    workflow_state: SparkExecutionWorkflowState
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, workflow_state: _Optional[_Union[SparkExecutionWorkflowState, str]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class SparkJobConfig(_message.Message):
    __slots__ = ["run_name", "spark_cluster_environment_version", "task", "execution_environment", "workspace_state_id", "tecton_runtime_version", "is_batch_compaction_fv"]
    RUN_NAME_FIELD_NUMBER: _ClassVar[int]
    SPARK_CLUSTER_ENVIRONMENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_STATE_ID_FIELD_NUMBER: _ClassVar[int]
    TECTON_RUNTIME_VERSION_FIELD_NUMBER: _ClassVar[int]
    IS_BATCH_COMPACTION_FV_FIELD_NUMBER: _ClassVar[int]
    run_name: str
    spark_cluster_environment_version: int
    task: _materialization_task__client_pb2.MaterializationTask
    execution_environment: _spark_cluster__client_pb2.SparkExecutionEnvironment
    workspace_state_id: _id__client_pb2.Id
    tecton_runtime_version: str
    is_batch_compaction_fv: bool
    def __init__(self, run_name: _Optional[str] = ..., spark_cluster_environment_version: _Optional[int] = ..., task: _Optional[_Union[_materialization_task__client_pb2.MaterializationTask, _Mapping]] = ..., execution_environment: _Optional[_Union[_spark_cluster__client_pb2.SparkExecutionEnvironment, str]] = ..., workspace_state_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., tecton_runtime_version: _Optional[str] = ..., is_batch_compaction_fv: bool = ...) -> None: ...

class RunResult(_message.Message):
    __slots__ = ["run_status", "termination_reason", "state_message", "is_permanent_failure"]
    RUN_STATUS_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_REASON_FIELD_NUMBER: _ClassVar[int]
    STATE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    IS_PERMANENT_FAILURE_FIELD_NUMBER: _ClassVar[int]
    run_status: _jobs__client_pb2.RunStatus
    termination_reason: _jobs__client_pb2.RunTerminationReason
    state_message: str
    is_permanent_failure: bool
    def __init__(self, run_status: _Optional[_Union[_jobs__client_pb2.RunStatus, str]] = ..., termination_reason: _Optional[_Union[_jobs__client_pb2.RunTerminationReason, str]] = ..., state_message: _Optional[str] = ..., is_permanent_failure: bool = ...) -> None: ...

class RunMetadata(_message.Message):
    __slots__ = ["run_id", "run_page_url"]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    run_page_url: str
    def __init__(self, run_id: _Optional[str] = ..., run_page_url: _Optional[str] = ...) -> None: ...

class SparkExecutionAttempt(_message.Message):
    __slots__ = ["run_metadata", "final_run_details", "state_transitions", "consumption_info", "consumption_start_time", "consumption_end_time", "consumption_scrape_watermark", "cluster_info"]
    RUN_METADATA_FIELD_NUMBER: _ClassVar[int]
    FINAL_RUN_DETAILS_FIELD_NUMBER: _ClassVar[int]
    STATE_TRANSITIONS_FIELD_NUMBER: _ClassVar[int]
    CONSUMPTION_INFO_FIELD_NUMBER: _ClassVar[int]
    CONSUMPTION_START_TIME_FIELD_NUMBER: _ClassVar[int]
    CONSUMPTION_END_TIME_FIELD_NUMBER: _ClassVar[int]
    CONSUMPTION_SCRAPE_WATERMARK_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_INFO_FIELD_NUMBER: _ClassVar[int]
    run_metadata: RunMetadata
    final_run_details: RunResult
    state_transitions: _containers.RepeatedCompositeFieldContainer[SparkExecutionAttemptStateTransition]
    consumption_info: _job_metadata__client_pb2.MaterializationConsumptionInfo
    consumption_start_time: _timestamp_pb2.Timestamp
    consumption_end_time: _timestamp_pb2.Timestamp
    consumption_scrape_watermark: _timestamp_pb2.Timestamp
    cluster_info: _clusters__client_pb2.ClusterInfo
    def __init__(self, run_metadata: _Optional[_Union[RunMetadata, _Mapping]] = ..., final_run_details: _Optional[_Union[RunResult, _Mapping]] = ..., state_transitions: _Optional[_Iterable[_Union[SparkExecutionAttemptStateTransition, _Mapping]]] = ..., consumption_info: _Optional[_Union[_job_metadata__client_pb2.MaterializationConsumptionInfo, _Mapping]] = ..., consumption_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., consumption_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., consumption_scrape_watermark: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cluster_info: _Optional[_Union[_clusters__client_pb2.ClusterInfo, _Mapping]] = ...) -> None: ...

class SparkExecutionAttemptStateTransition(_message.Message):
    __slots__ = ["attempt_state", "timestamp"]
    ATTEMPT_STATE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    attempt_state: SparkExecutionAttemptState
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, attempt_state: _Optional[_Union[SparkExecutionAttemptState, str]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
