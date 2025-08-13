from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JobType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    JOB_TYPE_UNSPECIFIED: _ClassVar[JobType]
    STREAM_MATERIALIZATION: _ClassVar[JobType]
    BATCH_MATERIALIZATION: _ClassVar[JobType]
    STREAM_PLAN_INTEGRATION_TEST: _ClassVar[JobType]
    BATCH_PLAN_INTEGRATION_TEST: _ClassVar[JobType]
    ENTITY_DELETION: _ClassVar[JobType]
    FEATURE_PUBLISH: _ClassVar[JobType]
    FEATURE_TABLE_INGEST: _ClassVar[JobType]
    DATASET_GENERATION: _ClassVar[JobType]
    OFFLINE_STORE_MAINTENANCE: _ClassVar[JobType]

class ComputeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    COMPUTE_TYPE_UNSPECIFIED: _ClassVar[ComputeType]
    EMR: _ClassVar[ComputeType]
    DATABRICKS: _ClassVar[ComputeType]
    RIFT: _ClassVar[ComputeType]

class ConsumptionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    CONSUMPTION_TYPE_UNSPECIFIED: _ClassVar[ConsumptionType]
    MATERIALIZATION_JOB_WRITES: _ClassVar[ConsumptionType]
    FEATURE_SERVER_READS: _ClassVar[ConsumptionType]
    RIFT_MATERIALIZATION_JOB_COMPUTE: _ClassVar[ConsumptionType]
    FEATURE_SERVER_NODE_DURATION: _ClassVar[ConsumptionType]
    SPARK_MATERIALIZATION_JOB_COMPUTE: _ClassVar[ConsumptionType]
    REAL_TIME_JOB_COMPUTE: _ClassVar[ConsumptionType]
    INGEST_API_COMPUTE: _ClassVar[ConsumptionType]
    SERVER_GROUP_NODE_DURATION: _ClassVar[ConsumptionType]
    FEATURE_SERVER_CACHE_USAGE: _ClassVar[ConsumptionType]

class ConsumptionUnit(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    CONSUMPTION_UNITS_UNSPECIFIED: _ClassVar[ConsumptionUnit]
    ONLINE_WRITE_ROWS: _ClassVar[ConsumptionUnit]
    OFFLINE_WRITE_ROWS: _ClassVar[ConsumptionUnit]
    OFFLINE_WRITE_VALUES: _ClassVar[ConsumptionUnit]
    TECTON_JOB_COMPUTE_HOURS: _ClassVar[ConsumptionUnit]
    FEATURE_SERVER_NODE_HOURS: _ClassVar[ConsumptionUnit]
    REAL_TIME_COMPUTE_DURATION_HOURS: _ClassVar[ConsumptionUnit]
    SERVER_GROUP_NODE_HOURS: _ClassVar[ConsumptionUnit]
    FEATURE_SERVICE_VECTORS_SERVED: _ClassVar[ConsumptionUnit]
    FEATURE_SERVICE_ONLINE_REQUESTS: _ClassVar[ConsumptionUnit]
    FEATURE_VIEW_ONLINE_READS: _ClassVar[ConsumptionUnit]
    FEATURE_SERVICE_ONLINE_VECTORS_SERVED: _ClassVar[ConsumptionUnit]
    FEATURE_SERVER_CACHE_NODE_HOURS: _ClassVar[ConsumptionUnit]

class Visibility(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    VISIBILITY_UNSPECIFIED: _ClassVar[Visibility]
    VISIBILITY_VISIBLE: _ClassVar[Visibility]

class Requirement(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    REQUIREMENT_UNSPECIFIED: _ClassVar[Requirement]
    REQUIREMENT_NOT_REQUIRED: _ClassVar[Requirement]
    REQUIREMENT_REQUIRED: _ClassVar[Requirement]

class ConsumptionServerGroupType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    CONSUMPTION_SERVER_GROUP_TYPE_UNSPECIFIED: _ClassVar[ConsumptionServerGroupType]
    TRANSFORM_SERVER_GROUP: _ClassVar[ConsumptionServerGroupType]
    FEATURE_SERVER_GROUP: _ClassVar[ConsumptionServerGroupType]
    INGEST_SERVER_GROUP: _ClassVar[ConsumptionServerGroupType]
JOB_TYPE_UNSPECIFIED: JobType
STREAM_MATERIALIZATION: JobType
BATCH_MATERIALIZATION: JobType
STREAM_PLAN_INTEGRATION_TEST: JobType
BATCH_PLAN_INTEGRATION_TEST: JobType
ENTITY_DELETION: JobType
FEATURE_PUBLISH: JobType
FEATURE_TABLE_INGEST: JobType
DATASET_GENERATION: JobType
OFFLINE_STORE_MAINTENANCE: JobType
COMPUTE_TYPE_UNSPECIFIED: ComputeType
EMR: ComputeType
DATABRICKS: ComputeType
RIFT: ComputeType
CONSUMPTION_TYPE_UNSPECIFIED: ConsumptionType
MATERIALIZATION_JOB_WRITES: ConsumptionType
FEATURE_SERVER_READS: ConsumptionType
RIFT_MATERIALIZATION_JOB_COMPUTE: ConsumptionType
FEATURE_SERVER_NODE_DURATION: ConsumptionType
SPARK_MATERIALIZATION_JOB_COMPUTE: ConsumptionType
REAL_TIME_JOB_COMPUTE: ConsumptionType
INGEST_API_COMPUTE: ConsumptionType
SERVER_GROUP_NODE_DURATION: ConsumptionType
FEATURE_SERVER_CACHE_USAGE: ConsumptionType
CONSUMPTION_UNITS_UNSPECIFIED: ConsumptionUnit
ONLINE_WRITE_ROWS: ConsumptionUnit
OFFLINE_WRITE_ROWS: ConsumptionUnit
OFFLINE_WRITE_VALUES: ConsumptionUnit
TECTON_JOB_COMPUTE_HOURS: ConsumptionUnit
FEATURE_SERVER_NODE_HOURS: ConsumptionUnit
REAL_TIME_COMPUTE_DURATION_HOURS: ConsumptionUnit
SERVER_GROUP_NODE_HOURS: ConsumptionUnit
FEATURE_SERVICE_VECTORS_SERVED: ConsumptionUnit
FEATURE_SERVICE_ONLINE_REQUESTS: ConsumptionUnit
FEATURE_VIEW_ONLINE_READS: ConsumptionUnit
FEATURE_SERVICE_ONLINE_VECTORS_SERVED: ConsumptionUnit
FEATURE_SERVER_CACHE_NODE_HOURS: ConsumptionUnit
VISIBILITY_UNSPECIFIED: Visibility
VISIBILITY_VISIBLE: Visibility
REQUIREMENT_UNSPECIFIED: Requirement
REQUIREMENT_NOT_REQUIRED: Requirement
REQUIREMENT_REQUIRED: Requirement
CONSUMPTION_SERVER_GROUP_TYPE_UNSPECIFIED: ConsumptionServerGroupType
TRANSFORM_SERVER_GROUP: ConsumptionServerGroupType
FEATURE_SERVER_GROUP: ConsumptionServerGroupType
INGEST_SERVER_GROUP: ConsumptionServerGroupType
BILLABLE_USAGE_OPTIONS_FIELD_NUMBER: _ClassVar[int]
billable_usage_options: _descriptor.FieldDescriptor

class ConsumptionInfo(_message.Message):
    __slots__ = ["time_bucket_start", "units_consumed", "metric", "details", "source_id", "feature_view_id", "feature_view_name", "workspace", "online_read_aws_region"]
    class DetailsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TIME_BUCKET_START_FIELD_NUMBER: _ClassVar[int]
    UNITS_CONSUMED_FIELD_NUMBER: _ClassVar[int]
    METRIC_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    ONLINE_READ_AWS_REGION_FIELD_NUMBER: _ClassVar[int]
    time_bucket_start: _timestamp_pb2.Timestamp
    units_consumed: int
    metric: str
    details: _containers.ScalarMap[str, str]
    source_id: str
    feature_view_id: _id__client_pb2.Id
    feature_view_name: str
    workspace: str
    online_read_aws_region: str
    def __init__(self, time_bucket_start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., units_consumed: _Optional[int] = ..., metric: _Optional[str] = ..., details: _Optional[_Mapping[str, str]] = ..., source_id: _Optional[str] = ..., feature_view_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., feature_view_name: _Optional[str] = ..., workspace: _Optional[str] = ..., online_read_aws_region: _Optional[str] = ...) -> None: ...

class EnrichedConsumptionInfo(_message.Message):
    __slots__ = ["consumption_info", "feature_view_workspace", "feature_view_name", "feature_view_id"]
    CONSUMPTION_INFO_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_ID_FIELD_NUMBER: _ClassVar[int]
    consumption_info: ConsumptionInfo
    feature_view_workspace: str
    feature_view_name: str
    feature_view_id: str
    def __init__(self, consumption_info: _Optional[_Union[ConsumptionInfo, _Mapping]] = ..., feature_view_workspace: _Optional[str] = ..., feature_view_name: _Optional[str] = ..., feature_view_id: _Optional[str] = ...) -> None: ...

class BillableUsageOptions(_message.Message):
    __slots__ = ["visibility", "required"]
    VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_FIELD_NUMBER: _ClassVar[int]
    visibility: Visibility
    required: Requirement
    def __init__(self, visibility: _Optional[_Union[Visibility, str]] = ..., required: _Optional[_Union[Requirement, str]] = ...) -> None: ...

class MaterializationJobOnlineWritesMetadata(_message.Message):
    __slots__ = ["online_store_type", "tecton_job_id", "workspace", "workspace_state_id", "tecton_object_name", "tecton_object_id", "tags"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ONLINE_STORE_TYPE_FIELD_NUMBER: _ClassVar[int]
    TECTON_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_STATE_ID_FIELD_NUMBER: _ClassVar[int]
    TECTON_OBJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    TECTON_OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    online_store_type: str
    tecton_job_id: str
    workspace: str
    workspace_state_id: str
    tecton_object_name: str
    tecton_object_id: str
    tags: _containers.ScalarMap[str, str]
    def __init__(self, online_store_type: _Optional[str] = ..., tecton_job_id: _Optional[str] = ..., workspace: _Optional[str] = ..., workspace_state_id: _Optional[str] = ..., tecton_object_name: _Optional[str] = ..., tecton_object_id: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class MaterializationJobOfflineWritesMetadata(_message.Message):
    __slots__ = ["tecton_job_id", "workspace", "workspace_state_id", "tecton_object_name", "tecton_object_id", "tags"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TECTON_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_STATE_ID_FIELD_NUMBER: _ClassVar[int]
    TECTON_OBJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    TECTON_OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    tecton_job_id: str
    workspace: str
    workspace_state_id: str
    tecton_object_name: str
    tecton_object_id: str
    tags: _containers.ScalarMap[str, str]
    def __init__(self, tecton_job_id: _Optional[str] = ..., workspace: _Optional[str] = ..., workspace_state_id: _Optional[str] = ..., tecton_object_name: _Optional[str] = ..., tecton_object_id: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class TectonJobComputeHoursMetadata(_message.Message):
    __slots__ = ["tecton_job_id", "instance_type", "region", "num_workers", "compute_type", "job_type", "workspace", "workspace_state_id", "tecton_object_name", "tecton_object_id", "tags"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TECTON_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    NUM_WORKERS_FIELD_NUMBER: _ClassVar[int]
    COMPUTE_TYPE_FIELD_NUMBER: _ClassVar[int]
    JOB_TYPE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_STATE_ID_FIELD_NUMBER: _ClassVar[int]
    TECTON_OBJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    TECTON_OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    tecton_job_id: str
    instance_type: str
    region: str
    num_workers: int
    compute_type: ComputeType
    job_type: JobType
    workspace: str
    workspace_state_id: str
    tecton_object_name: str
    tecton_object_id: str
    tags: _containers.ScalarMap[str, str]
    def __init__(self, tecton_job_id: _Optional[str] = ..., instance_type: _Optional[str] = ..., region: _Optional[str] = ..., num_workers: _Optional[int] = ..., compute_type: _Optional[_Union[ComputeType, str]] = ..., job_type: _Optional[_Union[JobType, str]] = ..., workspace: _Optional[str] = ..., workspace_state_id: _Optional[str] = ..., tecton_object_name: _Optional[str] = ..., tecton_object_id: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class IngestApiComputeHoursMetadata(_message.Message):
    __slots__ = ["compute_type", "job_type", "operation", "memory_mib", "workspace", "workspace_state_id", "tecton_object_name", "tecton_object_id", "tags"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    COMPUTE_TYPE_FIELD_NUMBER: _ClassVar[int]
    JOB_TYPE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    MEMORY_MIB_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_STATE_ID_FIELD_NUMBER: _ClassVar[int]
    TECTON_OBJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    TECTON_OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    compute_type: ComputeType
    job_type: JobType
    operation: str
    memory_mib: int
    workspace: str
    workspace_state_id: str
    tecton_object_name: str
    tecton_object_id: str
    tags: _containers.ScalarMap[str, str]
    def __init__(self, compute_type: _Optional[_Union[ComputeType, str]] = ..., job_type: _Optional[_Union[JobType, str]] = ..., operation: _Optional[str] = ..., memory_mib: _Optional[int] = ..., workspace: _Optional[str] = ..., workspace_state_id: _Optional[str] = ..., tecton_object_name: _Optional[str] = ..., tecton_object_id: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class FeatureServerNodeHoursMetadata(_message.Message):
    __slots__ = ["region", "pod_cpu", "pod_memory_mib", "pod_count"]
    REGION_FIELD_NUMBER: _ClassVar[int]
    POD_CPU_FIELD_NUMBER: _ClassVar[int]
    POD_MEMORY_MIB_FIELD_NUMBER: _ClassVar[int]
    POD_COUNT_FIELD_NUMBER: _ClassVar[int]
    region: str
    pod_cpu: float
    pod_memory_mib: int
    pod_count: int
    def __init__(self, region: _Optional[str] = ..., pod_cpu: _Optional[float] = ..., pod_memory_mib: _Optional[int] = ..., pod_count: _Optional[int] = ...) -> None: ...

class FeatureServerReadsMetadata(_message.Message):
    __slots__ = ["workspace", "tecton_object_name", "tecton_object_id", "owner", "tags"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    TECTON_OBJECT_NAME_FIELD_NUMBER: _ClassVar[int]
    TECTON_OBJECT_ID_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    tecton_object_name: str
    tecton_object_id: str
    owner: str
    tags: _containers.ScalarMap[str, str]
    def __init__(self, workspace: _Optional[str] = ..., tecton_object_name: _Optional[str] = ..., tecton_object_id: _Optional[str] = ..., owner: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ServerGroupNodeHoursMetadata(_message.Message):
    __slots__ = ["region", "instance_type", "server_group_name", "workspace", "cloud_provider", "server_group_type"]
    REGION_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SERVER_GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    CLOUD_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    SERVER_GROUP_TYPE_FIELD_NUMBER: _ClassVar[int]
    region: str
    instance_type: str
    server_group_name: str
    workspace: str
    cloud_provider: str
    server_group_type: ConsumptionServerGroupType
    def __init__(self, region: _Optional[str] = ..., instance_type: _Optional[str] = ..., server_group_name: _Optional[str] = ..., workspace: _Optional[str] = ..., cloud_provider: _Optional[str] = ..., server_group_type: _Optional[_Union[ConsumptionServerGroupType, str]] = ...) -> None: ...

class FeatureServerCacheUsageMetadata(_message.Message):
    __slots__ = ["region", "instance_type", "replication_group_id", "replication_group_arn"]
    REGION_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    REPLICATION_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    REPLICATION_GROUP_ARN_FIELD_NUMBER: _ClassVar[int]
    region: str
    instance_type: str
    replication_group_id: str
    replication_group_arn: str
    def __init__(self, region: _Optional[str] = ..., instance_type: _Optional[str] = ..., replication_group_id: _Optional[str] = ..., replication_group_arn: _Optional[str] = ...) -> None: ...

class ConsumptionRecord(_message.Message):
    __slots__ = ["timestamp", "collection_timestamp", "duration", "account_name", "materialization_job_online_writes_metadata", "materialization_job_offline_writes_metadata", "feature_server_node_hours_metadata", "feature_server_reads_metadata", "tecton_job_compute_hours_metadata", "ingest_api_compute_hours_metadata", "server_group_node_hours_metadata", "feature_server_cache_usage_metadata", "quantity", "unit", "is_canary", "tecton_credits", "tecton_dollars"]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    COLLECTION_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_NAME_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_JOB_ONLINE_WRITES_METADATA_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_JOB_OFFLINE_WRITES_METADATA_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVER_NODE_HOURS_METADATA_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVER_READS_METADATA_FIELD_NUMBER: _ClassVar[int]
    TECTON_JOB_COMPUTE_HOURS_METADATA_FIELD_NUMBER: _ClassVar[int]
    INGEST_API_COMPUTE_HOURS_METADATA_FIELD_NUMBER: _ClassVar[int]
    SERVER_GROUP_NODE_HOURS_METADATA_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVER_CACHE_USAGE_METADATA_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    UNIT_FIELD_NUMBER: _ClassVar[int]
    IS_CANARY_FIELD_NUMBER: _ClassVar[int]
    TECTON_CREDITS_FIELD_NUMBER: _ClassVar[int]
    TECTON_DOLLARS_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    collection_timestamp: _timestamp_pb2.Timestamp
    duration: _duration_pb2.Duration
    account_name: str
    materialization_job_online_writes_metadata: MaterializationJobOnlineWritesMetadata
    materialization_job_offline_writes_metadata: MaterializationJobOfflineWritesMetadata
    feature_server_node_hours_metadata: FeatureServerNodeHoursMetadata
    feature_server_reads_metadata: FeatureServerReadsMetadata
    tecton_job_compute_hours_metadata: TectonJobComputeHoursMetadata
    ingest_api_compute_hours_metadata: IngestApiComputeHoursMetadata
    server_group_node_hours_metadata: ServerGroupNodeHoursMetadata
    feature_server_cache_usage_metadata: FeatureServerCacheUsageMetadata
    quantity: float
    unit: ConsumptionUnit
    is_canary: bool
    tecton_credits: float
    tecton_dollars: float
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., collection_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., account_name: _Optional[str] = ..., materialization_job_online_writes_metadata: _Optional[_Union[MaterializationJobOnlineWritesMetadata, _Mapping]] = ..., materialization_job_offline_writes_metadata: _Optional[_Union[MaterializationJobOfflineWritesMetadata, _Mapping]] = ..., feature_server_node_hours_metadata: _Optional[_Union[FeatureServerNodeHoursMetadata, _Mapping]] = ..., feature_server_reads_metadata: _Optional[_Union[FeatureServerReadsMetadata, _Mapping]] = ..., tecton_job_compute_hours_metadata: _Optional[_Union[TectonJobComputeHoursMetadata, _Mapping]] = ..., ingest_api_compute_hours_metadata: _Optional[_Union[IngestApiComputeHoursMetadata, _Mapping]] = ..., server_group_node_hours_metadata: _Optional[_Union[ServerGroupNodeHoursMetadata, _Mapping]] = ..., feature_server_cache_usage_metadata: _Optional[_Union[FeatureServerCacheUsageMetadata, _Mapping]] = ..., quantity: _Optional[float] = ..., unit: _Optional[_Union[ConsumptionUnit, str]] = ..., is_canary: bool = ..., tecton_credits: _Optional[float] = ..., tecton_dollars: _Optional[float] = ...) -> None: ...
