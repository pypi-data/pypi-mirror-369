from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.args import feature_view__client_pb2 as _feature_view__client_pb2
from tecton_proto.auth import service__client_pb2 as _service__client_pb2
from tecton_proto.common import compute_identity__client_pb2 as _compute_identity__client_pb2
from tecton_proto.common import compute_mode__client_pb2 as _compute_mode__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import schema__client_pb2 as _schema__client_pb2
from tecton_proto.materialization import spark_cluster__client_pb2 as _spark_cluster__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TestOnlyMaterializationJobType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    TEST_ONLY_MATERIALIZATION_JOB_TYPE_UNSPECIFIED: _ClassVar[TestOnlyMaterializationJobType]
    TEST_ONLY_MATERIALIZATION_JOB_TYPE_BATCH: _ClassVar[TestOnlyMaterializationJobType]
    TEST_ONLY_MATERIALIZATION_JOB_TYPE_STREAM: _ClassVar[TestOnlyMaterializationJobType]
    TEST_ONLY_MATERIALIZATION_JOB_TYPE_INGEST: _ClassVar[TestOnlyMaterializationJobType]
    TEST_ONLY_MATERIALIZATION_JOB_TYPE_MAINTENANCE: _ClassVar[TestOnlyMaterializationJobType]
    TEST_ONLY_MATERIALIZATION_JOB_TYPE_DATASET_GENERATION: _ClassVar[TestOnlyMaterializationJobType]
    TEST_ONLY_MATERIALIZATION_JOB_TYPE_ICEBERG_MAINTENANCE: _ClassVar[TestOnlyMaterializationJobType]
TEST_ONLY_MATERIALIZATION_JOB_TYPE_UNSPECIFIED: TestOnlyMaterializationJobType
TEST_ONLY_MATERIALIZATION_JOB_TYPE_BATCH: TestOnlyMaterializationJobType
TEST_ONLY_MATERIALIZATION_JOB_TYPE_STREAM: TestOnlyMaterializationJobType
TEST_ONLY_MATERIALIZATION_JOB_TYPE_INGEST: TestOnlyMaterializationJobType
TEST_ONLY_MATERIALIZATION_JOB_TYPE_MAINTENANCE: TestOnlyMaterializationJobType
TEST_ONLY_MATERIALIZATION_JOB_TYPE_DATASET_GENERATION: TestOnlyMaterializationJobType
TEST_ONLY_MATERIALIZATION_JOB_TYPE_ICEBERG_MAINTENANCE: TestOnlyMaterializationJobType

class MaterializationJobRequest(_message.Message):
    __slots__ = ["workspace", "feature_view", "start_time", "end_time", "online", "offline", "use_tecton_managed_retries", "overwrite"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_FIELD_NUMBER: _ClassVar[int]
    USE_TECTON_MANAGED_RETRIES_FIELD_NUMBER: _ClassVar[int]
    OVERWRITE_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    feature_view: str
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    online: bool
    offline: bool
    use_tecton_managed_retries: bool
    overwrite: bool
    def __init__(self, workspace: _Optional[str] = ..., feature_view: _Optional[str] = ..., start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., online: bool = ..., offline: bool = ..., use_tecton_managed_retries: bool = ..., overwrite: bool = ...) -> None: ...

class MaterializationJobResponse(_message.Message):
    __slots__ = ["job"]
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: MaterializationJob
    def __init__(self, job: _Optional[_Union[MaterializationJob, _Mapping]] = ...) -> None: ...

class MaterializationJob(_message.Message):
    __slots__ = ["id", "workspace", "feature_view", "feature_service", "saved_feature_data_frame", "start_time", "end_time", "created_at", "updated_at", "state", "attempts", "next_attempt_at", "online", "offline", "job_type", "ingest_path"]
    ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_FIELD_NUMBER: _ClassVar[int]
    SAVED_FEATURE_DATA_FRAME_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    NEXT_ATTEMPT_AT_FIELD_NUMBER: _ClassVar[int]
    ONLINE_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_FIELD_NUMBER: _ClassVar[int]
    JOB_TYPE_FIELD_NUMBER: _ClassVar[int]
    INGEST_PATH_FIELD_NUMBER: _ClassVar[int]
    id: str
    workspace: str
    feature_view: str
    feature_service: str
    saved_feature_data_frame: str
    start_time: _timestamp_pb2.Timestamp
    end_time: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    state: str
    attempts: _containers.RepeatedCompositeFieldContainer[JobAttempt]
    next_attempt_at: _timestamp_pb2.Timestamp
    online: bool
    offline: bool
    job_type: str
    ingest_path: str
    def __init__(self, id: _Optional[str] = ..., workspace: _Optional[str] = ..., feature_view: _Optional[str] = ..., feature_service: _Optional[str] = ..., saved_feature_data_frame: _Optional[str] = ..., start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., state: _Optional[str] = ..., attempts: _Optional[_Iterable[_Union[JobAttempt, _Mapping]]] = ..., next_attempt_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., online: bool = ..., offline: bool = ..., job_type: _Optional[str] = ..., ingest_path: _Optional[str] = ...) -> None: ...

class JobAttempt(_message.Message):
    __slots__ = ["id", "created_at", "updated_at", "state", "run_url", "compute_identity", "duration"]
    ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    RUN_URL_FIELD_NUMBER: _ClassVar[int]
    COMPUTE_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    id: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    state: str
    run_url: str
    compute_identity: _compute_identity__client_pb2.ComputeIdentity
    duration: _duration_pb2.Duration
    def __init__(self, id: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., state: _Optional[str] = ..., run_url: _Optional[str] = ..., compute_identity: _Optional[_Union[_compute_identity__client_pb2.ComputeIdentity, _Mapping]] = ..., duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class ListJobsRequest(_message.Message):
    __slots__ = ["workspace", "feature_view", "feature_service"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    feature_view: str
    feature_service: str
    def __init__(self, workspace: _Optional[str] = ..., feature_view: _Optional[str] = ..., feature_service: _Optional[str] = ...) -> None: ...

class ListJobsResponse(_message.Message):
    __slots__ = ["jobs"]
    JOBS_FIELD_NUMBER: _ClassVar[int]
    jobs: _containers.RepeatedCompositeFieldContainer[MaterializationJob]
    def __init__(self, jobs: _Optional[_Iterable[_Union[MaterializationJob, _Mapping]]] = ...) -> None: ...

class GetJobRequest(_message.Message):
    __slots__ = ["job_id", "workspace", "feature_view", "feature_service"]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    workspace: str
    feature_view: str
    feature_service: str
    def __init__(self, job_id: _Optional[str] = ..., workspace: _Optional[str] = ..., feature_view: _Optional[str] = ..., feature_service: _Optional[str] = ...) -> None: ...

class GetJobResponse(_message.Message):
    __slots__ = ["job"]
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: MaterializationJob
    def __init__(self, job: _Optional[_Union[MaterializationJob, _Mapping]] = ...) -> None: ...

class CancelJobRequest(_message.Message):
    __slots__ = ["job_id", "workspace", "feature_view", "feature_service"]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_FIELD_NUMBER: _ClassVar[int]
    job_id: str
    workspace: str
    feature_view: str
    feature_service: str
    def __init__(self, job_id: _Optional[str] = ..., workspace: _Optional[str] = ..., feature_view: _Optional[str] = ..., feature_service: _Optional[str] = ...) -> None: ...

class CancelJobResponse(_message.Message):
    __slots__ = ["job"]
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: MaterializationJob
    def __init__(self, job: _Optional[_Union[MaterializationJob, _Mapping]] = ...) -> None: ...

class GetLatestReadyTimeRequest(_message.Message):
    __slots__ = ["workspace", "feature_view", "feature_service"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    feature_view: str
    feature_service: str
    def __init__(self, workspace: _Optional[str] = ..., feature_view: _Optional[str] = ..., feature_service: _Optional[str] = ...) -> None: ...

class GetLatestReadyTimeResponse(_message.Message):
    __slots__ = ["online_latest_ready_time", "offline_latest_ready_time"]
    ONLINE_LATEST_READY_TIME_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_LATEST_READY_TIME_FIELD_NUMBER: _ClassVar[int]
    online_latest_ready_time: _timestamp_pb2.Timestamp
    offline_latest_ready_time: _timestamp_pb2.Timestamp
    def __init__(self, online_latest_ready_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., offline_latest_ready_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TestOnlyGetMaterializationTaskParamsRequest(_message.Message):
    __slots__ = ["workspace", "feature_view_name", "job_type", "disable_offline", "disable_online", "job_start_time", "job_end_time", "df_path"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_TYPE_FIELD_NUMBER: _ClassVar[int]
    DISABLE_OFFLINE_FIELD_NUMBER: _ClassVar[int]
    DISABLE_ONLINE_FIELD_NUMBER: _ClassVar[int]
    JOB_START_TIME_FIELD_NUMBER: _ClassVar[int]
    JOB_END_TIME_FIELD_NUMBER: _ClassVar[int]
    DF_PATH_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    feature_view_name: str
    job_type: TestOnlyMaterializationJobType
    disable_offline: bool
    disable_online: bool
    job_start_time: _timestamp_pb2.Timestamp
    job_end_time: _timestamp_pb2.Timestamp
    df_path: str
    def __init__(self, workspace: _Optional[str] = ..., feature_view_name: _Optional[str] = ..., job_type: _Optional[_Union[TestOnlyMaterializationJobType, str]] = ..., disable_offline: bool = ..., disable_online: bool = ..., job_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., job_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., df_path: _Optional[str] = ...) -> None: ...

class TestOnlyGetDatasetGenerationTaskParamsRequest(_message.Message):
    __slots__ = ["start_dataset_job_request"]
    START_DATASET_JOB_REQUEST_FIELD_NUMBER: _ClassVar[int]
    start_dataset_job_request: StartDatasetJobRequest
    def __init__(self, start_dataset_job_request: _Optional[_Union[StartDatasetJobRequest, _Mapping]] = ...) -> None: ...

class TestOnlyGetMaterializationTaskParamsResponse(_message.Message):
    __slots__ = ["encoded_materialization_params"]
    ENCODED_MATERIALIZATION_PARAMS_FIELD_NUMBER: _ClassVar[int]
    encoded_materialization_params: str
    def __init__(self, encoded_materialization_params: _Optional[str] = ...) -> None: ...

class GetDataframeInfoRequest(_message.Message):
    __slots__ = ["feature_view", "feature_service", "workspace", "task_type"]
    FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    feature_view: str
    feature_service: str
    workspace: str
    task_type: _spark_cluster__client_pb2.TaskType
    def __init__(self, feature_view: _Optional[str] = ..., feature_service: _Optional[str] = ..., workspace: _Optional[str] = ..., task_type: _Optional[_Union[_spark_cluster__client_pb2.TaskType, str]] = ...) -> None: ...

class GetDataframeUploadUrlRequest(_message.Message):
    __slots__ = ["feature_view", "feature_service", "workspace", "task_type"]
    FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    feature_view: str
    feature_service: str
    workspace: str
    task_type: _spark_cluster__client_pb2.TaskType
    def __init__(self, feature_view: _Optional[str] = ..., feature_service: _Optional[str] = ..., workspace: _Optional[str] = ..., task_type: _Optional[_Union[_spark_cluster__client_pb2.TaskType, str]] = ...) -> None: ...

class GetDataframeUploadUrlResponse(_message.Message):
    __slots__ = ["key", "upload_id"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    key: str
    upload_id: str
    def __init__(self, key: _Optional[str] = ..., upload_id: _Optional[str] = ...) -> None: ...

class UploadDataframePartRequest(_message.Message):
    __slots__ = ["workspace", "key", "parent_upload_id", "part_number"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    PARENT_UPLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    PART_NUMBER_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    key: str
    parent_upload_id: str
    part_number: int
    def __init__(self, workspace: _Optional[str] = ..., key: _Optional[str] = ..., parent_upload_id: _Optional[str] = ..., part_number: _Optional[int] = ...) -> None: ...

class UploadDataframePartResponse(_message.Message):
    __slots__ = ["upload_url"]
    UPLOAD_URL_FIELD_NUMBER: _ClassVar[int]
    upload_url: str
    def __init__(self, upload_url: _Optional[str] = ...) -> None: ...

class CompleteDataframeUploadRequest(_message.Message):
    __slots__ = ["workspace", "key", "upload_id", "part_etags"]
    class PartEtagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: str
        def __init__(self, key: _Optional[int] = ..., value: _Optional[str] = ...) -> None: ...
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    PART_ETAGS_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    key: str
    upload_id: str
    part_etags: _containers.ScalarMap[int, str]
    def __init__(self, workspace: _Optional[str] = ..., key: _Optional[str] = ..., upload_id: _Optional[str] = ..., part_etags: _Optional[_Mapping[int, str]] = ...) -> None: ...

class CompleteDataframeUploadResponse(_message.Message):
    __slots__ = ["key"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    key: str
    def __init__(self, key: _Optional[str] = ...) -> None: ...

class GetDataframeInfoResponse(_message.Message):
    __slots__ = ["df_path", "signed_url_for_df_upload"]
    DF_PATH_FIELD_NUMBER: _ClassVar[int]
    SIGNED_URL_FOR_DF_UPLOAD_FIELD_NUMBER: _ClassVar[int]
    df_path: str
    signed_url_for_df_upload: str
    def __init__(self, df_path: _Optional[str] = ..., signed_url_for_df_upload: _Optional[str] = ...) -> None: ...

class IngestDataframeFromS3Request(_message.Message):
    __slots__ = ["feature_view", "df_path", "workspace", "use_tecton_managed_retries"]
    FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    DF_PATH_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    USE_TECTON_MANAGED_RETRIES_FIELD_NUMBER: _ClassVar[int]
    feature_view: str
    df_path: str
    workspace: str
    use_tecton_managed_retries: bool
    def __init__(self, feature_view: _Optional[str] = ..., df_path: _Optional[str] = ..., workspace: _Optional[str] = ..., use_tecton_managed_retries: bool = ...) -> None: ...

class IngestDataframeFromS3Response(_message.Message):
    __slots__ = ["job"]
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: MaterializationJob
    def __init__(self, job: _Optional[_Union[MaterializationJob, _Mapping]] = ...) -> None: ...

class StartDatasetJobRequest(_message.Message):
    __slots__ = ["compute_mode", "from_source", "workspace", "feature_service_id", "feature_view_id", "spine", "datetime_range", "dataset_name", "cluster_config", "tecton_runtime", "environment", "extra_config", "expected_schema", "job_retry_times"]
    class SpineInput(_message.Message):
        __slots__ = ["path", "timestamp_key", "column_names"]
        PATH_FIELD_NUMBER: _ClassVar[int]
        TIMESTAMP_KEY_FIELD_NUMBER: _ClassVar[int]
        COLUMN_NAMES_FIELD_NUMBER: _ClassVar[int]
        path: str
        timestamp_key: str
        column_names: _containers.RepeatedScalarFieldContainer[str]
        def __init__(self, path: _Optional[str] = ..., timestamp_key: _Optional[str] = ..., column_names: _Optional[_Iterable[str]] = ...) -> None: ...
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
    class ExtraConfigEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    COMPUTE_MODE_FIELD_NUMBER: _ClassVar[int]
    FROM_SOURCE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_ID_FIELD_NUMBER: _ClassVar[int]
    SPINE_FIELD_NUMBER: _ClassVar[int]
    DATETIME_RANGE_FIELD_NUMBER: _ClassVar[int]
    DATASET_NAME_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    TECTON_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    EXTRA_CONFIG_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    JOB_RETRY_TIMES_FIELD_NUMBER: _ClassVar[int]
    compute_mode: _compute_mode__client_pb2.BatchComputeMode
    from_source: bool
    workspace: str
    feature_service_id: _id__client_pb2.Id
    feature_view_id: _id__client_pb2.Id
    spine: StartDatasetJobRequest.SpineInput
    datetime_range: StartDatasetJobRequest.DateTimeRangeInput
    dataset_name: str
    cluster_config: _feature_view__client_pb2.ClusterConfig
    tecton_runtime: str
    environment: str
    extra_config: _containers.ScalarMap[str, str]
    expected_schema: _schema__client_pb2.Schema
    job_retry_times: int
    def __init__(self, compute_mode: _Optional[_Union[_compute_mode__client_pb2.BatchComputeMode, str]] = ..., from_source: bool = ..., workspace: _Optional[str] = ..., feature_service_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., feature_view_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., spine: _Optional[_Union[StartDatasetJobRequest.SpineInput, _Mapping]] = ..., datetime_range: _Optional[_Union[StartDatasetJobRequest.DateTimeRangeInput, _Mapping]] = ..., dataset_name: _Optional[str] = ..., cluster_config: _Optional[_Union[_feature_view__client_pb2.ClusterConfig, _Mapping]] = ..., tecton_runtime: _Optional[str] = ..., environment: _Optional[str] = ..., extra_config: _Optional[_Mapping[str, str]] = ..., expected_schema: _Optional[_Union[_schema__client_pb2.Schema, _Mapping]] = ..., job_retry_times: _Optional[int] = ...) -> None: ...

class StartDatasetJobResponse(_message.Message):
    __slots__ = ["job"]
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: MaterializationJob
    def __init__(self, job: _Optional[_Union[MaterializationJob, _Mapping]] = ...) -> None: ...

class CancelDatasetJobRequest(_message.Message):
    __slots__ = ["workspace", "saved_feature_data_frame", "job_id"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    SAVED_FEATURE_DATA_FRAME_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    saved_feature_data_frame: str
    job_id: str
    def __init__(self, workspace: _Optional[str] = ..., saved_feature_data_frame: _Optional[str] = ..., job_id: _Optional[str] = ...) -> None: ...

class CancelDatasetJobResponse(_message.Message):
    __slots__ = ["job"]
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: MaterializationJob
    def __init__(self, job: _Optional[_Union[MaterializationJob, _Mapping]] = ...) -> None: ...

class GetDatasetJobRequest(_message.Message):
    __slots__ = ["workspace", "saved_feature_data_frame", "job_id"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    SAVED_FEATURE_DATA_FRAME_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    saved_feature_data_frame: str
    job_id: str
    def __init__(self, workspace: _Optional[str] = ..., saved_feature_data_frame: _Optional[str] = ..., job_id: _Optional[str] = ...) -> None: ...

class GetDatasetJobResponse(_message.Message):
    __slots__ = ["job"]
    JOB_FIELD_NUMBER: _ClassVar[int]
    job: MaterializationJob
    def __init__(self, job: _Optional[_Union[MaterializationJob, _Mapping]] = ...) -> None: ...

class TestOnlyWriteFeatureServerConfigRequest(_message.Message):
    __slots__ = ["absolute_filepath", "transform_server_filepath", "workspace"]
    ABSOLUTE_FILEPATH_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_SERVER_FILEPATH_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    absolute_filepath: str
    transform_server_filepath: str
    workspace: str
    def __init__(self, absolute_filepath: _Optional[str] = ..., transform_server_filepath: _Optional[str] = ..., workspace: _Optional[str] = ...) -> None: ...

class TestOnlyWriteFeatureServerConfigResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class TestOnlyOnlineTableNameRequest(_message.Message):
    __slots__ = ["workspace", "feature_view_name", "watermark"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    WATERMARK_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    feature_view_name: str
    watermark: _timestamp_pb2.Timestamp
    def __init__(self, workspace: _Optional[str] = ..., feature_view_name: _Optional[str] = ..., watermark: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class TestOnlyOnlineTableNameResponse(_message.Message):
    __slots__ = ["table_name"]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    table_name: str
    def __init__(self, table_name: _Optional[str] = ...) -> None: ...

class TestOnlyCompleteOnlineTableRequest(_message.Message):
    __slots__ = ["workspace", "feature_view_name"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    feature_view_name: str
    def __init__(self, workspace: _Optional[str] = ..., feature_view_name: _Optional[str] = ...) -> None: ...

class TestOnlyCompleteOnlineTableResponse(_message.Message):
    __slots__ = ["table_name"]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    table_name: str
    def __init__(self, table_name: _Optional[str] = ...) -> None: ...
