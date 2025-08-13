from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.args import diff_options__client_pb2 as _diff_options__client_pb2
from tecton_proto.args import feature_view__client_pb2 as _feature_view__client_pb2
from tecton_proto.common import compute_mode__client_pb2 as _compute_mode__client_pb2
from tecton_proto.common import fco_locator__client_pb2 as _fco_locator__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import schema__client_pb2 as _schema__client_pb2
from tecton_proto.data import batch_data_source__client_pb2 as _batch_data_source__client_pb2
from tecton_proto.materialization import materialization_states__client_pb2 as _materialization_states__client_pb2
from tecton_proto.materialization import spark_cluster__client_pb2 as _spark_cluster__client_pb2
from tecton_proto.online_store_writer import config__client_pb2 as _config__client_pb2
from tecton_proto.snowflake import location__client_pb2 as _location__client_pb2
from tecton_proto.spark_api import jobs__client_pb2 as _jobs__client_pb2
from tecton_proto.spark_common import libraries__client_pb2 as _libraries__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class MaterializationTaskStateTransition(_message.Message):
    __slots__ = ["task_state", "timestamp"]
    TASK_STATE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    task_state: _materialization_states__client_pb2.MaterializationTaskState
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, task_state: _Optional[_Union[_materialization_states__client_pb2.MaterializationTaskState, str]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class MaterializationTaskDep(_message.Message):
    __slots__ = ["offline_store_dependency"]
    OFFLINE_STORE_DEPENDENCY_FIELD_NUMBER: _ClassVar[int]
    offline_store_dependency: OfflineStoreDependency
    def __init__(self, offline_store_dependency: _Optional[_Union[OfflineStoreDependency, _Mapping]] = ...) -> None: ...

class OfflineStoreDependency(_message.Message):
    __slots__ = ["feature_start_time", "feature_end_time"]
    FEATURE_START_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_END_TIME_FIELD_NUMBER: _ClassVar[int]
    feature_start_time: _timestamp_pb2.Timestamp
    feature_end_time: _timestamp_pb2.Timestamp
    def __init__(self, feature_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class BatchMaterializationParameters(_message.Message):
    __slots__ = ["window_start_time", "window_end_time", "feature_start_time", "feature_end_time", "tile_count", "write_to_online_feature_store", "write_to_offline_feature_store", "is_overwrite_backfill", "bootstraps_online_store", "read_from_offline_store_for_online_write", "create_online_table", "create_online_table_parameters", "batch_compaction_enabled", "is_overwrite", "task_dependencies"]
    WINDOW_START_TIME_FIELD_NUMBER: _ClassVar[int]
    WINDOW_END_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_START_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_END_TIME_FIELD_NUMBER: _ClassVar[int]
    TILE_COUNT_FIELD_NUMBER: _ClassVar[int]
    WRITE_TO_ONLINE_FEATURE_STORE_FIELD_NUMBER: _ClassVar[int]
    WRITE_TO_OFFLINE_FEATURE_STORE_FIELD_NUMBER: _ClassVar[int]
    IS_OVERWRITE_BACKFILL_FIELD_NUMBER: _ClassVar[int]
    BOOTSTRAPS_ONLINE_STORE_FIELD_NUMBER: _ClassVar[int]
    READ_FROM_OFFLINE_STORE_FOR_ONLINE_WRITE_FIELD_NUMBER: _ClassVar[int]
    CREATE_ONLINE_TABLE_FIELD_NUMBER: _ClassVar[int]
    CREATE_ONLINE_TABLE_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    BATCH_COMPACTION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    IS_OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    TASK_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    window_start_time: _timestamp_pb2.Timestamp
    window_end_time: _timestamp_pb2.Timestamp
    feature_start_time: _timestamp_pb2.Timestamp
    feature_end_time: _timestamp_pb2.Timestamp
    tile_count: int
    write_to_online_feature_store: bool
    write_to_offline_feature_store: bool
    is_overwrite_backfill: bool
    bootstraps_online_store: bool
    read_from_offline_store_for_online_write: bool
    create_online_table: bool
    create_online_table_parameters: CreateOnlineTableParameters
    batch_compaction_enabled: bool
    is_overwrite: bool
    task_dependencies: MaterializationTaskDep
    def __init__(self, window_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., window_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., tile_count: _Optional[int] = ..., write_to_online_feature_store: bool = ..., write_to_offline_feature_store: bool = ..., is_overwrite_backfill: bool = ..., bootstraps_online_store: bool = ..., read_from_offline_store_for_online_write: bool = ..., create_online_table: bool = ..., create_online_table_parameters: _Optional[_Union[CreateOnlineTableParameters, _Mapping]] = ..., batch_compaction_enabled: bool = ..., is_overwrite: bool = ..., task_dependencies: _Optional[_Union[MaterializationTaskDep, _Mapping]] = ...) -> None: ...

class CreateOnlineTableParameters(_message.Message):
    __slots__ = ["import_path_prefix"]
    IMPORT_PATH_PREFIX_FIELD_NUMBER: _ClassVar[int]
    import_path_prefix: str
    def __init__(self, import_path_prefix: _Optional[str] = ...) -> None: ...

class IngestMaterializationParameters(_message.Message):
    __slots__ = ["write_to_online_feature_store", "write_to_offline_feature_store", "ingest_path"]
    WRITE_TO_ONLINE_FEATURE_STORE_FIELD_NUMBER: _ClassVar[int]
    WRITE_TO_OFFLINE_FEATURE_STORE_FIELD_NUMBER: _ClassVar[int]
    INGEST_PATH_FIELD_NUMBER: _ClassVar[int]
    write_to_online_feature_store: bool
    write_to_offline_feature_store: bool
    ingest_path: str
    def __init__(self, write_to_online_feature_store: bool = ..., write_to_offline_feature_store: bool = ..., ingest_path: _Optional[str] = ...) -> None: ...

class DeletionParameters(_message.Message):
    __slots__ = ["online_join_keys_path", "online_join_keys_full_path", "offline_join_keys_path", "online", "offline"]
    ONLINE_JOIN_KEYS_PATH_FIELD_NUMBER: _ClassVar[int]
    ONLINE_JOIN_KEYS_FULL_PATH_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_JOIN_KEYS_PATH_FIELD_NUMBER: _ClassVar[int]
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_FIELD_NUMBER: _ClassVar[int]
    online_join_keys_path: str
    online_join_keys_full_path: str
    offline_join_keys_path: str
    online: bool
    offline: bool
    def __init__(self, online_join_keys_path: _Optional[str] = ..., online_join_keys_full_path: _Optional[str] = ..., offline_join_keys_path: _Optional[str] = ..., online: bool = ..., offline: bool = ...) -> None: ...

class DeltaMaintenanceParameters(_message.Message):
    __slots__ = ["generate_manifest", "period_end", "execute_compaction", "vacuum", "execute_sorting", "vacuum_retention_hours", "entity_sample_rows"]
    GENERATE_MANIFEST_FIELD_NUMBER: _ClassVar[int]
    PERIOD_END_FIELD_NUMBER: _ClassVar[int]
    EXECUTE_COMPACTION_FIELD_NUMBER: _ClassVar[int]
    VACUUM_FIELD_NUMBER: _ClassVar[int]
    EXECUTE_SORTING_FIELD_NUMBER: _ClassVar[int]
    VACUUM_RETENTION_HOURS_FIELD_NUMBER: _ClassVar[int]
    ENTITY_SAMPLE_ROWS_FIELD_NUMBER: _ClassVar[int]
    generate_manifest: bool
    period_end: _timestamp_pb2.Timestamp
    execute_compaction: bool
    vacuum: bool
    execute_sorting: bool
    vacuum_retention_hours: int
    entity_sample_rows: int
    def __init__(self, generate_manifest: bool = ..., period_end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., execute_compaction: bool = ..., vacuum: bool = ..., execute_sorting: bool = ..., vacuum_retention_hours: _Optional[int] = ..., entity_sample_rows: _Optional[int] = ...) -> None: ...

class IcebergMaintenanceParameters(_message.Message):
    __slots__ = ["execute_compaction", "period_end"]
    EXECUTE_COMPACTION_FIELD_NUMBER: _ClassVar[int]
    PERIOD_END_FIELD_NUMBER: _ClassVar[int]
    execute_compaction: bool
    period_end: _timestamp_pb2.Timestamp
    def __init__(self, execute_compaction: bool = ..., period_end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class StreamMaterializationParameters(_message.Message):
    __slots__ = ["stream_handoff_config"]
    STREAM_HANDOFF_CONFIG_FIELD_NUMBER: _ClassVar[int]
    stream_handoff_config: StreamHandoffConfig
    def __init__(self, stream_handoff_config: _Optional[_Union[StreamHandoffConfig, _Mapping]] = ...) -> None: ...

class FeatureExportParameters(_message.Message):
    __slots__ = ["parent_materialization_task_id", "feature_start_time", "feature_end_time", "export_store_path"]
    PARENT_MATERIALIZATION_TASK_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_START_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_END_TIME_FIELD_NUMBER: _ClassVar[int]
    EXPORT_STORE_PATH_FIELD_NUMBER: _ClassVar[int]
    parent_materialization_task_id: _id__client_pb2.Id
    feature_start_time: _timestamp_pb2.Timestamp
    feature_end_time: _timestamp_pb2.Timestamp
    export_store_path: str
    def __init__(self, parent_materialization_task_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., feature_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., export_store_path: _Optional[str] = ...) -> None: ...

class DatasetGenerationParameters(_message.Message):
    __slots__ = ["from_source", "feature_service", "feature_view", "dataset", "dataset_name", "spine", "datetime_range", "batch_config", "result_path", "cluster_config", "extra_config", "expected_schema", "job_retry_times"]
    class SpineInput(_message.Message):
        __slots__ = ["path", "timestamp_key"]
        PATH_FIELD_NUMBER: _ClassVar[int]
        TIMESTAMP_KEY_FIELD_NUMBER: _ClassVar[int]
        path: str
        timestamp_key: str
        def __init__(self, path: _Optional[str] = ..., timestamp_key: _Optional[str] = ...) -> None: ...
    class DateTimeRangeInput(_message.Message):
        __slots__ = ["start", "end", "max_lookback", "entities_path"]
        START_FIELD_NUMBER: _ClassVar[int]
        END_FIELD_NUMBER: _ClassVar[int]
        MAX_LOOKBACK_FIELD_NUMBER: _ClassVar[int]
        ENTITIES_PATH_FIELD_NUMBER: _ClassVar[int]
        start: _timestamp_pb2.Timestamp
        end: _timestamp_pb2.Timestamp
        max_lookback: _timestamp_pb2.Timestamp
        entities_path: str
        def __init__(self, start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., max_lookback: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., entities_path: _Optional[str] = ...) -> None: ...
    class BatchConfigInput(_message.Message):
        __slots__ = ["batch_source", "start", "end"]
        BATCH_SOURCE_FIELD_NUMBER: _ClassVar[int]
        START_FIELD_NUMBER: _ClassVar[int]
        END_FIELD_NUMBER: _ClassVar[int]
        batch_source: _batch_data_source__client_pb2.BatchDataSource
        start: _timestamp_pb2.Timestamp
        end: _timestamp_pb2.Timestamp
        def __init__(self, batch_source: _Optional[_Union[_batch_data_source__client_pb2.BatchDataSource, _Mapping]] = ..., start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    class ExtraConfigEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    FROM_SOURCE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    DATASET_FIELD_NUMBER: _ClassVar[int]
    DATASET_NAME_FIELD_NUMBER: _ClassVar[int]
    SPINE_FIELD_NUMBER: _ClassVar[int]
    DATETIME_RANGE_FIELD_NUMBER: _ClassVar[int]
    BATCH_CONFIG_FIELD_NUMBER: _ClassVar[int]
    RESULT_PATH_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    EXTRA_CONFIG_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    JOB_RETRY_TIMES_FIELD_NUMBER: _ClassVar[int]
    from_source: bool
    feature_service: _fco_locator__client_pb2.IdFcoLocator
    feature_view: _fco_locator__client_pb2.IdFcoLocator
    dataset: _fco_locator__client_pb2.IdFcoLocator
    dataset_name: str
    spine: DatasetGenerationParameters.SpineInput
    datetime_range: DatasetGenerationParameters.DateTimeRangeInput
    batch_config: DatasetGenerationParameters.BatchConfigInput
    result_path: str
    cluster_config: _feature_view__client_pb2.ClusterConfig
    extra_config: _containers.ScalarMap[str, str]
    expected_schema: _schema__client_pb2.Schema
    job_retry_times: int
    def __init__(self, from_source: bool = ..., feature_service: _Optional[_Union[_fco_locator__client_pb2.IdFcoLocator, _Mapping]] = ..., feature_view: _Optional[_Union[_fco_locator__client_pb2.IdFcoLocator, _Mapping]] = ..., dataset: _Optional[_Union[_fco_locator__client_pb2.IdFcoLocator, _Mapping]] = ..., dataset_name: _Optional[str] = ..., spine: _Optional[_Union[DatasetGenerationParameters.SpineInput, _Mapping]] = ..., datetime_range: _Optional[_Union[DatasetGenerationParameters.DateTimeRangeInput, _Mapping]] = ..., batch_config: _Optional[_Union[DatasetGenerationParameters.BatchConfigInput, _Mapping]] = ..., result_path: _Optional[str] = ..., cluster_config: _Optional[_Union[_feature_view__client_pb2.ClusterConfig, _Mapping]] = ..., extra_config: _Optional[_Mapping[str, str]] = ..., expected_schema: _Optional[_Union[_schema__client_pb2.Schema, _Mapping]] = ..., job_retry_times: _Optional[int] = ...) -> None: ...

class StreamHandoffConfig(_message.Message):
    __slots__ = ["enabled", "previous_task_id"]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    PREVIOUS_TASK_ID_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    previous_task_id: _id__client_pb2.Id
    def __init__(self, enabled: bool = ..., previous_task_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ...) -> None: ...

class MaterializationTask(_message.Message):
    __slots__ = ["materialization_task_id", "plan_id", "id_feature_view_locator", "id_feature_service_locator", "materialization_serial_version", "tecton_runtime_version", "tecton_environment", "compute_mode", "batch_parameters", "stream_parameters", "ingest_parameters", "deletion_parameters", "delta_maintenance_parameters", "feature_export_parameters", "dataset_generation_parameters", "iceberg_maintenance_parameters", "spark_cluster_environment_version", "state_transitions", "number_of_attempts_from_old_executions", "error_message", "created_at", "updated_at", "attempts", "canary_params", "manually_triggered", "managed_retries", "attempt_status_message"]
    MATERIALIZATION_TASK_ID_FIELD_NUMBER: _ClassVar[int]
    PLAN_ID_FIELD_NUMBER: _ClassVar[int]
    ID_FEATURE_VIEW_LOCATOR_FIELD_NUMBER: _ClassVar[int]
    ID_FEATURE_SERVICE_LOCATOR_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_SERIAL_VERSION_FIELD_NUMBER: _ClassVar[int]
    TECTON_RUNTIME_VERSION_FIELD_NUMBER: _ClassVar[int]
    TECTON_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    COMPUTE_MODE_FIELD_NUMBER: _ClassVar[int]
    BATCH_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    STREAM_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    INGEST_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    DELETION_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    DELTA_MAINTENANCE_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_EXPORT_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    DATASET_GENERATION_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    ICEBERG_MAINTENANCE_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    SPARK_CLUSTER_ENVIRONMENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    STATE_TRANSITIONS_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_ATTEMPTS_FROM_OLD_EXECUTIONS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    CANARY_PARAMS_FIELD_NUMBER: _ClassVar[int]
    MANUALLY_TRIGGERED_FIELD_NUMBER: _ClassVar[int]
    MANAGED_RETRIES_FIELD_NUMBER: _ClassVar[int]
    ATTEMPT_STATUS_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    materialization_task_id: _id__client_pb2.Id
    plan_id: _id__client_pb2.Id
    id_feature_view_locator: _fco_locator__client_pb2.IdFcoLocator
    id_feature_service_locator: _fco_locator__client_pb2.IdFcoLocator
    materialization_serial_version: int
    tecton_runtime_version: str
    tecton_environment: str
    compute_mode: _compute_mode__client_pb2.BatchComputeMode
    batch_parameters: BatchMaterializationParameters
    stream_parameters: StreamMaterializationParameters
    ingest_parameters: IngestMaterializationParameters
    deletion_parameters: DeletionParameters
    delta_maintenance_parameters: DeltaMaintenanceParameters
    feature_export_parameters: FeatureExportParameters
    dataset_generation_parameters: DatasetGenerationParameters
    iceberg_maintenance_parameters: IcebergMaintenanceParameters
    spark_cluster_environment_version: int
    state_transitions: _containers.RepeatedCompositeFieldContainer[MaterializationTaskStateTransition]
    number_of_attempts_from_old_executions: int
    error_message: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    attempts: _containers.RepeatedCompositeFieldContainer[Attempt]
    canary_params: CanaryParams
    manually_triggered: bool
    managed_retries: bool
    attempt_status_message: str
    def __init__(self, materialization_task_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., plan_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., id_feature_view_locator: _Optional[_Union[_fco_locator__client_pb2.IdFcoLocator, _Mapping]] = ..., id_feature_service_locator: _Optional[_Union[_fco_locator__client_pb2.IdFcoLocator, _Mapping]] = ..., materialization_serial_version: _Optional[int] = ..., tecton_runtime_version: _Optional[str] = ..., tecton_environment: _Optional[str] = ..., compute_mode: _Optional[_Union[_compute_mode__client_pb2.BatchComputeMode, str]] = ..., batch_parameters: _Optional[_Union[BatchMaterializationParameters, _Mapping]] = ..., stream_parameters: _Optional[_Union[StreamMaterializationParameters, _Mapping]] = ..., ingest_parameters: _Optional[_Union[IngestMaterializationParameters, _Mapping]] = ..., deletion_parameters: _Optional[_Union[DeletionParameters, _Mapping]] = ..., delta_maintenance_parameters: _Optional[_Union[DeltaMaintenanceParameters, _Mapping]] = ..., feature_export_parameters: _Optional[_Union[FeatureExportParameters, _Mapping]] = ..., dataset_generation_parameters: _Optional[_Union[DatasetGenerationParameters, _Mapping]] = ..., iceberg_maintenance_parameters: _Optional[_Union[IcebergMaintenanceParameters, _Mapping]] = ..., spark_cluster_environment_version: _Optional[int] = ..., state_transitions: _Optional[_Iterable[_Union[MaterializationTaskStateTransition, _Mapping]]] = ..., number_of_attempts_from_old_executions: _Optional[int] = ..., error_message: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., attempts: _Optional[_Iterable[_Union[Attempt, _Mapping]]] = ..., canary_params: _Optional[_Union[CanaryParams, _Mapping]] = ..., manually_triggered: bool = ..., managed_retries: bool = ..., attempt_status_message: _Optional[str] = ...) -> None: ...

class CanaryParams(_message.Message):
    __slots__ = ["canary_id", "canary_online_config", "canary_streaming_checkpoint_path", "canary_library_overrides", "canary_spark_cluster_environment", "canary_run_name"]
    CANARY_ID_FIELD_NUMBER: _ClassVar[int]
    CANARY_ONLINE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CANARY_STREAMING_CHECKPOINT_PATH_FIELD_NUMBER: _ClassVar[int]
    CANARY_LIBRARY_OVERRIDES_FIELD_NUMBER: _ClassVar[int]
    CANARY_SPARK_CLUSTER_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    CANARY_RUN_NAME_FIELD_NUMBER: _ClassVar[int]
    canary_id: str
    canary_online_config: _config__client_pb2.OnlineStoreWriterConfiguration
    canary_streaming_checkpoint_path: str
    canary_library_overrides: _containers.RepeatedCompositeFieldContainer[_libraries__client_pb2.Library]
    canary_spark_cluster_environment: _spark_cluster__client_pb2.SparkClusterEnvironment
    canary_run_name: str
    def __init__(self, canary_id: _Optional[str] = ..., canary_online_config: _Optional[_Union[_config__client_pb2.OnlineStoreWriterConfiguration, _Mapping]] = ..., canary_streaming_checkpoint_path: _Optional[str] = ..., canary_library_overrides: _Optional[_Iterable[_Union[_libraries__client_pb2.Library, _Mapping]]] = ..., canary_spark_cluster_environment: _Optional[_Union[_spark_cluster__client_pb2.SparkClusterEnvironment, _Mapping]] = ..., canary_run_name: _Optional[str] = ...) -> None: ...

class Attempt(_message.Message):
    __slots__ = ["workflow_id", "has_legacy_materialization_task_attempt"]
    WORKFLOW_ID_FIELD_NUMBER: _ClassVar[int]
    HAS_LEGACY_MATERIALIZATION_TASK_ATTEMPT_FIELD_NUMBER: _ClassVar[int]
    workflow_id: _id__client_pb2.Id
    has_legacy_materialization_task_attempt: bool
    def __init__(self, workflow_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., has_legacy_materialization_task_attempt: bool = ...) -> None: ...

class MaterializationTaskAttemptStateTransition(_message.Message):
    __slots__ = ["attempt_state", "state_message", "termination_reason", "timestamp"]
    ATTEMPT_STATE_FIELD_NUMBER: _ClassVar[int]
    STATE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_REASON_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    attempt_state: _materialization_states__client_pb2.MaterializationTaskAttemptState
    state_message: str
    termination_reason: _jobs__client_pb2.RunTerminationReason
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, attempt_state: _Optional[_Union[_materialization_states__client_pb2.MaterializationTaskAttemptState, str]] = ..., state_message: _Optional[str] = ..., termination_reason: _Optional[_Union[_jobs__client_pb2.RunTerminationReason, str]] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class MaterializationTaskAttempt(_message.Message):
    __slots__ = ["materialization_task_attempt_id", "materialization_task_id", "execution_environment", "run_id", "run_page_url", "state_transitions", "attempt_number", "created_at", "updated_at", "cluster_config", "online_store_copier_tasks", "snowflake_data"]
    class OnlineStoreCopierTasksEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: OnlineStoreCopierTask
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[OnlineStoreCopierTask, _Mapping]] = ...) -> None: ...
    MATERIALIZATION_TASK_ATTEMPT_ID_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_TASK_ID_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    STATE_TRANSITIONS_FIELD_NUMBER: _ClassVar[int]
    ATTEMPT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ONLINE_STORE_COPIER_TASKS_FIELD_NUMBER: _ClassVar[int]
    SNOWFLAKE_DATA_FIELD_NUMBER: _ClassVar[int]
    materialization_task_attempt_id: _id__client_pb2.Id
    materialization_task_id: _id__client_pb2.Id
    execution_environment: _spark_cluster__client_pb2.SparkExecutionEnvironment
    run_id: str
    run_page_url: str
    state_transitions: _containers.RepeatedCompositeFieldContainer[MaterializationTaskAttemptStateTransition]
    attempt_number: int
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    cluster_config: _feature_view__client_pb2.ClusterConfig
    online_store_copier_tasks: _containers.MessageMap[str, OnlineStoreCopierTask]
    snowflake_data: SnowflakeData
    def __init__(self, materialization_task_attempt_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., materialization_task_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., execution_environment: _Optional[_Union[_spark_cluster__client_pb2.SparkExecutionEnvironment, str]] = ..., run_id: _Optional[str] = ..., run_page_url: _Optional[str] = ..., state_transitions: _Optional[_Iterable[_Union[MaterializationTaskAttemptStateTransition, _Mapping]]] = ..., attempt_number: _Optional[int] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., cluster_config: _Optional[_Union[_feature_view__client_pb2.ClusterConfig, _Mapping]] = ..., online_store_copier_tasks: _Optional[_Mapping[str, OnlineStoreCopierTask]] = ..., snowflake_data: _Optional[_Union[SnowflakeData, _Mapping]] = ...) -> None: ...

class OnlineStoreCopierTaskStateTransition(_message.Message):
    __slots__ = ["state", "state_message", "timestamp"]
    STATE_FIELD_NUMBER: _ClassVar[int]
    STATE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    state: _materialization_states__client_pb2.OnlineStoreCopierTaskState
    state_message: str
    timestamp: _timestamp_pb2.Timestamp
    def __init__(self, state: _Optional[_Union[_materialization_states__client_pb2.OnlineStoreCopierTaskState, str]] = ..., state_message: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class OnlineStoreCopierTask(_message.Message):
    __slots__ = ["attempts", "total_rows", "completed_rows", "last_progress_request_id", "last_progress_send_time"]
    ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ROWS_FIELD_NUMBER: _ClassVar[int]
    COMPLETED_ROWS_FIELD_NUMBER: _ClassVar[int]
    LAST_PROGRESS_REQUEST_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_PROGRESS_SEND_TIME_FIELD_NUMBER: _ClassVar[int]
    attempts: _containers.RepeatedCompositeFieldContainer[OnlineStoreCopierTaskAttempt]
    total_rows: int
    completed_rows: int
    last_progress_request_id: str
    last_progress_send_time: _timestamp_pb2.Timestamp
    def __init__(self, attempts: _Optional[_Iterable[_Union[OnlineStoreCopierTaskAttempt, _Mapping]]] = ..., total_rows: _Optional[int] = ..., completed_rows: _Optional[int] = ..., last_progress_request_id: _Optional[str] = ..., last_progress_send_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class OnlineStoreCopierTaskAttempt(_message.Message):
    __slots__ = ["state_transitions"]
    STATE_TRANSITIONS_FIELD_NUMBER: _ClassVar[int]
    state_transitions: _containers.RepeatedCompositeFieldContainer[OnlineStoreCopierTaskStateTransition]
    def __init__(self, state_transitions: _Optional[_Iterable[_Union[OnlineStoreCopierTaskStateTransition, _Mapping]]] = ...) -> None: ...

class SnowflakeData(_message.Message):
    __slots__ = ["base_location", "total_online_rows", "total_offline_rows"]
    BASE_LOCATION_FIELD_NUMBER: _ClassVar[int]
    TOTAL_ONLINE_ROWS_FIELD_NUMBER: _ClassVar[int]
    TOTAL_OFFLINE_ROWS_FIELD_NUMBER: _ClassVar[int]
    base_location: _location__client_pb2.StageLocation
    total_online_rows: int
    total_offline_rows: int
    def __init__(self, base_location: _Optional[_Union[_location__client_pb2.StageLocation, _Mapping]] = ..., total_online_rows: _Optional[int] = ..., total_offline_rows: _Optional[int] = ...) -> None: ...
