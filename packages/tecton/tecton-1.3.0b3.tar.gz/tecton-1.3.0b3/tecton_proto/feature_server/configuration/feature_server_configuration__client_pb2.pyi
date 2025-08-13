from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.args import feature_view__client_pb2 as _feature_view__client_pb2
from tecton_proto.args import pipeline__client_pb2 as _pipeline__client_pb2
from tecton_proto.args import transformation__client_pb2 as _transformation__client_pb2
from tecton_proto.args import user_defined_function__client_pb2 as _user_defined_function__client_pb2
from tecton_proto.auth import acl__client_pb2 as _acl__client_pb2
from tecton_proto.common import aggregation_function__client_pb2 as _aggregation_function__client_pb2
from tecton_proto.common import calculation_node__client_pb2 as _calculation_node__client_pb2
from tecton_proto.common import data_type__client_pb2 as _data_type__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import schema__client_pb2 as _schema__client_pb2
from tecton_proto.common import time_window__client_pb2 as _time_window__client_pb2
from tecton_proto.data import feature_service__client_pb2 as _feature_service__client_pb2
from tecton_proto.data import feature_view__client_pb2 as _feature_view__client_pb2_1
from tecton_proto.data import realtime_compute__client_pb2 as _realtime_compute__client_pb2
from tecton_proto.data import tecton_api_key__client_pb2 as _tecton_api_key__client_pb2
from tecton_proto.data import transformation__client_pb2 as _transformation__client_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataTableTimestampType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    DATA_TABLE_TIMESTAMP_TYPE_UNKNOWN: _ClassVar[DataTableTimestampType]
    DATA_TABLE_TIMESTAMP_TYPE_SORT_KEY: _ClassVar[DataTableTimestampType]
    DATA_TABLE_TIMESTAMP_TYPE_ATTRIBUTE: _ClassVar[DataTableTimestampType]

class StatusTableTimestampType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    STATUS_TABLE_TIMESTAMP_TYPE_UNKNOWN: _ClassVar[StatusTableTimestampType]
    STATUS_TABLE_TIMESTAMP_TYPE_SORT_KEY: _ClassVar[StatusTableTimestampType]
    STATUS_TABLE_TIMESTAMP_TYPE_ATTRIBUTE: _ClassVar[StatusTableTimestampType]
    STATUS_TABLE_TIMESTAMP_CONTINUOUS_AGGREGATE: _ClassVar[StatusTableTimestampType]
DATA_TABLE_TIMESTAMP_TYPE_UNKNOWN: DataTableTimestampType
DATA_TABLE_TIMESTAMP_TYPE_SORT_KEY: DataTableTimestampType
DATA_TABLE_TIMESTAMP_TYPE_ATTRIBUTE: DataTableTimestampType
STATUS_TABLE_TIMESTAMP_TYPE_UNKNOWN: StatusTableTimestampType
STATUS_TABLE_TIMESTAMP_TYPE_SORT_KEY: StatusTableTimestampType
STATUS_TABLE_TIMESTAMP_TYPE_ATTRIBUTE: StatusTableTimestampType
STATUS_TABLE_TIMESTAMP_CONTINUOUS_AGGREGATE: StatusTableTimestampType

class FeaturesPlan(_message.Message):
    __slots__ = ["feature_plan", "realtime_features_plan"]
    FEATURE_PLAN_FIELD_NUMBER: _ClassVar[int]
    REALTIME_FEATURES_PLAN_FIELD_NUMBER: _ClassVar[int]
    feature_plan: FeaturePlan
    realtime_features_plan: RealtimeFeaturesPlan
    def __init__(self, feature_plan: _Optional[_Union[FeaturePlan, _Mapping]] = ..., realtime_features_plan: _Optional[_Union[RealtimeFeaturesPlan, _Mapping]] = ...) -> None: ...

class Column(_message.Message):
    __slots__ = ["data_type", "feature_view_space_name", "feature_service_space_name", "feature_view_index", "batch_table_feature_view_index", "description", "tags", "abstract_syntax_tree_root", "input_column_name"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_SPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_SPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_INDEX_FIELD_NUMBER: _ClassVar[int]
    BATCH_TABLE_FEATURE_VIEW_INDEX_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    ABSTRACT_SYNTAX_TREE_ROOT_FIELD_NUMBER: _ClassVar[int]
    INPUT_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    data_type: _data_type__client_pb2.DataType
    feature_view_space_name: str
    feature_service_space_name: str
    feature_view_index: int
    batch_table_feature_view_index: int
    description: str
    tags: _containers.ScalarMap[str, str]
    abstract_syntax_tree_root: _calculation_node__client_pb2.AbstractSyntaxTreeNode
    input_column_name: str
    def __init__(self, data_type: _Optional[_Union[_data_type__client_pb2.DataType, _Mapping]] = ..., feature_view_space_name: _Optional[str] = ..., feature_service_space_name: _Optional[str] = ..., feature_view_index: _Optional[int] = ..., batch_table_feature_view_index: _Optional[int] = ..., description: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ..., abstract_syntax_tree_root: _Optional[_Union[_calculation_node__client_pb2.AbstractSyntaxTreeNode, _Mapping]] = ..., input_column_name: _Optional[str] = ...) -> None: ...

class FeaturePlan(_message.Message):
    __slots__ = ["output_column", "input_columns", "aggregation_function", "aggregation_function_params", "aggregation_window", "join_keys", "wildcard_join_keys", "aggregation_secondary_key", "is_secondary_key_output", "table_name", "data_table_timestamp_type", "status_table_timestamp_type", "timestamp_key", "slide_period", "serving_ttl", "refresh_status_table", "feature_view_name", "feature_view_id", "feature_store_format_version", "online_store_params", "deletionTimeWindow", "time_window", "feature_view_cache_config", "cache_index", "table_format_version", "batch_table_name", "batch_table_window_index", "stream_table_name", "tiles", "is_compacted_feature_view", "feature_set_column_hash", "aggregation_leading_edge_mode"]
    OUTPUT_COLUMN_FIELD_NUMBER: _ClassVar[int]
    INPUT_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_FUNCTION_PARAMS_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_WINDOW_FIELD_NUMBER: _ClassVar[int]
    JOIN_KEYS_FIELD_NUMBER: _ClassVar[int]
    WILDCARD_JOIN_KEYS_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_SECONDARY_KEY_FIELD_NUMBER: _ClassVar[int]
    IS_SECONDARY_KEY_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    DATA_TABLE_TIMESTAMP_TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_TABLE_TIMESTAMP_TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_KEY_FIELD_NUMBER: _ClassVar[int]
    SLIDE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    SERVING_TTL_FIELD_NUMBER: _ClassVar[int]
    REFRESH_STATUS_TABLE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_STORE_FORMAT_VERSION_FIELD_NUMBER: _ClassVar[int]
    ONLINE_STORE_PARAMS_FIELD_NUMBER: _ClassVar[int]
    DELETIONTIMEWINDOW_FIELD_NUMBER: _ClassVar[int]
    TIME_WINDOW_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_CACHE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CACHE_INDEX_FIELD_NUMBER: _ClassVar[int]
    TABLE_FORMAT_VERSION_FIELD_NUMBER: _ClassVar[int]
    BATCH_TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    BATCH_TABLE_WINDOW_INDEX_FIELD_NUMBER: _ClassVar[int]
    STREAM_TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    TILES_FIELD_NUMBER: _ClassVar[int]
    IS_COMPACTED_FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SET_COLUMN_HASH_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_LEADING_EDGE_MODE_FIELD_NUMBER: _ClassVar[int]
    output_column: Column
    input_columns: _containers.RepeatedCompositeFieldContainer[Column]
    aggregation_function: _aggregation_function__client_pb2.AggregationFunction
    aggregation_function_params: _aggregation_function__client_pb2.AggregationFunctionParams
    aggregation_window: _duration_pb2.Duration
    join_keys: _containers.RepeatedCompositeFieldContainer[Column]
    wildcard_join_keys: _containers.RepeatedCompositeFieldContainer[Column]
    aggregation_secondary_key: Column
    is_secondary_key_output: bool
    table_name: str
    data_table_timestamp_type: DataTableTimestampType
    status_table_timestamp_type: StatusTableTimestampType
    timestamp_key: str
    slide_period: _duration_pb2.Duration
    serving_ttl: _duration_pb2.Duration
    refresh_status_table: bool
    feature_view_name: str
    feature_view_id: str
    feature_store_format_version: int
    online_store_params: _feature_view__client_pb2_1.OnlineStoreParams
    deletionTimeWindow: int
    time_window: _time_window__client_pb2.TimeWindow
    feature_view_cache_config: _feature_view__client_pb2_1.FeatureViewCacheConfig
    cache_index: int
    table_format_version: int
    batch_table_name: str
    batch_table_window_index: int
    stream_table_name: str
    tiles: _containers.RepeatedCompositeFieldContainer[_schema__client_pb2.OnlineBatchTablePartTile]
    is_compacted_feature_view: bool
    feature_set_column_hash: str
    aggregation_leading_edge_mode: _feature_view__client_pb2.AggregationLeadingEdge
    def __init__(self, output_column: _Optional[_Union[Column, _Mapping]] = ..., input_columns: _Optional[_Iterable[_Union[Column, _Mapping]]] = ..., aggregation_function: _Optional[_Union[_aggregation_function__client_pb2.AggregationFunction, str]] = ..., aggregation_function_params: _Optional[_Union[_aggregation_function__client_pb2.AggregationFunctionParams, _Mapping]] = ..., aggregation_window: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., join_keys: _Optional[_Iterable[_Union[Column, _Mapping]]] = ..., wildcard_join_keys: _Optional[_Iterable[_Union[Column, _Mapping]]] = ..., aggregation_secondary_key: _Optional[_Union[Column, _Mapping]] = ..., is_secondary_key_output: bool = ..., table_name: _Optional[str] = ..., data_table_timestamp_type: _Optional[_Union[DataTableTimestampType, str]] = ..., status_table_timestamp_type: _Optional[_Union[StatusTableTimestampType, str]] = ..., timestamp_key: _Optional[str] = ..., slide_period: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., serving_ttl: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., refresh_status_table: bool = ..., feature_view_name: _Optional[str] = ..., feature_view_id: _Optional[str] = ..., feature_store_format_version: _Optional[int] = ..., online_store_params: _Optional[_Union[_feature_view__client_pb2_1.OnlineStoreParams, _Mapping]] = ..., deletionTimeWindow: _Optional[int] = ..., time_window: _Optional[_Union[_time_window__client_pb2.TimeWindow, _Mapping]] = ..., feature_view_cache_config: _Optional[_Union[_feature_view__client_pb2_1.FeatureViewCacheConfig, _Mapping]] = ..., cache_index: _Optional[int] = ..., table_format_version: _Optional[int] = ..., batch_table_name: _Optional[str] = ..., batch_table_window_index: _Optional[int] = ..., stream_table_name: _Optional[str] = ..., tiles: _Optional[_Iterable[_Union[_schema__client_pb2.OnlineBatchTablePartTile, _Mapping]]] = ..., is_compacted_feature_view: bool = ..., feature_set_column_hash: _Optional[str] = ..., aggregation_leading_edge_mode: _Optional[_Union[_feature_view__client_pb2.AggregationLeadingEdge, str]] = ...) -> None: ...

class FeatureVectorPlan(_message.Message):
    __slots__ = ["features"]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    features: _containers.RepeatedCompositeFieldContainer[FeaturePlan]
    def __init__(self, features: _Optional[_Iterable[_Union[FeaturePlan, _Mapping]]] = ...) -> None: ...

class RealtimeFeaturesPlan(_message.Message):
    __slots__ = ["args_from_request_context", "outputs", "feature_set_inputs", "pipeline", "transformations", "feature_view_name", "feature_view_id", "compact_transformations", "description", "tags"]
    class FeatureSetInputsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: FeatureVectorPlan
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[FeatureVectorPlan, _Mapping]] = ...) -> None: ...
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ARGS_FROM_REQUEST_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    OUTPUTS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SET_INPUTS_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_FIELD_NUMBER: _ClassVar[int]
    TRANSFORMATIONS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_ID_FIELD_NUMBER: _ClassVar[int]
    COMPACT_TRANSFORMATIONS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    args_from_request_context: _containers.RepeatedCompositeFieldContainer[Column]
    outputs: _containers.RepeatedCompositeFieldContainer[Column]
    feature_set_inputs: _containers.MessageMap[str, FeatureVectorPlan]
    pipeline: _pipeline__client_pb2.Pipeline
    transformations: _containers.RepeatedCompositeFieldContainer[_transformation__client_pb2_1.Transformation]
    feature_view_name: str
    feature_view_id: str
    compact_transformations: _containers.RepeatedCompositeFieldContainer[CompactTransformation]
    description: str
    tags: _containers.ScalarMap[str, str]
    def __init__(self, args_from_request_context: _Optional[_Iterable[_Union[Column, _Mapping]]] = ..., outputs: _Optional[_Iterable[_Union[Column, _Mapping]]] = ..., feature_set_inputs: _Optional[_Mapping[str, FeatureVectorPlan]] = ..., pipeline: _Optional[_Union[_pipeline__client_pb2.Pipeline, _Mapping]] = ..., transformations: _Optional[_Iterable[_Union[_transformation__client_pb2_1.Transformation, _Mapping]]] = ..., feature_view_name: _Optional[str] = ..., feature_view_id: _Optional[str] = ..., compact_transformations: _Optional[_Iterable[_Union[CompactTransformation, _Mapping]]] = ..., description: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class CompactTransformation(_message.Message):
    __slots__ = ["transformation_id", "transformation_mode", "user_defined_function_id"]
    TRANSFORMATION_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSFORMATION_MODE_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_FUNCTION_ID_FIELD_NUMBER: _ClassVar[int]
    transformation_id: _id__client_pb2.Id
    transformation_mode: _transformation__client_pb2.TransformationMode
    user_defined_function_id: str
    def __init__(self, transformation_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., transformation_mode: _Optional[_Union[_transformation__client_pb2.TransformationMode, str]] = ..., user_defined_function_id: _Optional[str] = ...) -> None: ...

class LoggingConfig(_message.Message):
    __slots__ = ["sample_rate", "log_effective_times", "avro_schema"]
    SAMPLE_RATE_FIELD_NUMBER: _ClassVar[int]
    LOG_EFFECTIVE_TIMES_FIELD_NUMBER: _ClassVar[int]
    AVRO_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    sample_rate: float
    log_effective_times: bool
    avro_schema: str
    def __init__(self, sample_rate: _Optional[float] = ..., log_effective_times: bool = ..., avro_schema: _Optional[str] = ...) -> None: ...

class FeatureServicePlan(_message.Message):
    __slots__ = ["feature_service_id", "feature_view_id", "feature_service_name", "feature_view_name", "workspace_name", "workspace_state_id", "features_plans", "join_key_template", "logging_config", "realtime_environment", "cache_plans"]
    FEATURE_SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_STATE_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURES_PLANS_FIELD_NUMBER: _ClassVar[int]
    JOIN_KEY_TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    LOGGING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    REALTIME_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    CACHE_PLANS_FIELD_NUMBER: _ClassVar[int]
    feature_service_id: _id__client_pb2.Id
    feature_view_id: _id__client_pb2.Id
    feature_service_name: str
    feature_view_name: str
    workspace_name: str
    workspace_state_id: _id__client_pb2.Id
    features_plans: _containers.RepeatedCompositeFieldContainer[FeaturesPlan]
    join_key_template: _feature_service__client_pb2.JoinKeyTemplate
    logging_config: LoggingConfig
    realtime_environment: _realtime_compute__client_pb2.OnlineComputeConfig
    cache_plans: _containers.RepeatedCompositeFieldContainer[FeatureServiceCachePlan]
    def __init__(self, feature_service_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., feature_view_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., feature_service_name: _Optional[str] = ..., feature_view_name: _Optional[str] = ..., workspace_name: _Optional[str] = ..., workspace_state_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., features_plans: _Optional[_Iterable[_Union[FeaturesPlan, _Mapping]]] = ..., join_key_template: _Optional[_Union[_feature_service__client_pb2.JoinKeyTemplate, _Mapping]] = ..., logging_config: _Optional[_Union[LoggingConfig, _Mapping]] = ..., realtime_environment: _Optional[_Union[_realtime_compute__client_pb2.OnlineComputeConfig, _Mapping]] = ..., cache_plans: _Optional[_Iterable[_Union[FeatureServiceCachePlan, _Mapping]]] = ...) -> None: ...

class GlobalTableConfig(_message.Message):
    __slots__ = ["feature_view_id", "feature_view_name", "workspace_name", "slide_period", "status_table_timestamp_type", "refresh_status_table", "feature_store_format_version", "online_store_params", "table_format_version", "feature_data_water_mark"]
    FEATURE_VIEW_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    SLIDE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    STATUS_TABLE_TIMESTAMP_TYPE_FIELD_NUMBER: _ClassVar[int]
    REFRESH_STATUS_TABLE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_STORE_FORMAT_VERSION_FIELD_NUMBER: _ClassVar[int]
    ONLINE_STORE_PARAMS_FIELD_NUMBER: _ClassVar[int]
    TABLE_FORMAT_VERSION_FIELD_NUMBER: _ClassVar[int]
    FEATURE_DATA_WATER_MARK_FIELD_NUMBER: _ClassVar[int]
    feature_view_id: _id__client_pb2.Id
    feature_view_name: str
    workspace_name: str
    slide_period: _duration_pb2.Duration
    status_table_timestamp_type: StatusTableTimestampType
    refresh_status_table: bool
    feature_store_format_version: int
    online_store_params: _feature_view__client_pb2_1.OnlineStoreParams
    table_format_version: int
    feature_data_water_mark: _timestamp_pb2.Timestamp
    def __init__(self, feature_view_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., feature_view_name: _Optional[str] = ..., workspace_name: _Optional[str] = ..., slide_period: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., status_table_timestamp_type: _Optional[_Union[StatusTableTimestampType, str]] = ..., refresh_status_table: bool = ..., feature_store_format_version: _Optional[int] = ..., online_store_params: _Optional[_Union[_feature_view__client_pb2_1.OnlineStoreParams, _Mapping]] = ..., table_format_version: _Optional[int] = ..., feature_data_water_mark: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class FeatureServiceAcls(_message.Message):
    __slots__ = ["feature_service_id", "acls"]
    FEATURE_SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
    ACLS_FIELD_NUMBER: _ClassVar[int]
    feature_service_id: _id__client_pb2.Id
    acls: _containers.RepeatedCompositeFieldContainer[_acl__client_pb2.Acl]
    def __init__(self, feature_service_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., acls: _Optional[_Iterable[_Union[_acl__client_pb2.Acl, _Mapping]]] = ...) -> None: ...

class WorkspaceAcls(_message.Message):
    __slots__ = ["workspace_name", "acls"]
    WORKSPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    ACLS_FIELD_NUMBER: _ClassVar[int]
    workspace_name: str
    acls: _containers.RepeatedCompositeFieldContainer[_acl__client_pb2.Acl]
    def __init__(self, workspace_name: _Optional[str] = ..., acls: _Optional[_Iterable[_Union[_acl__client_pb2.Acl, _Mapping]]] = ...) -> None: ...

class CanaryConfig(_message.Message):
    __slots__ = ["feature_server_canary_id", "feature_server_canary_pod_name", "feature_server_canary_follower_endpoint"]
    FEATURE_SERVER_CANARY_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVER_CANARY_POD_NAME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVER_CANARY_FOLLOWER_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    feature_server_canary_id: str
    feature_server_canary_pod_name: str
    feature_server_canary_follower_endpoint: str
    def __init__(self, feature_server_canary_id: _Optional[str] = ..., feature_server_canary_pod_name: _Optional[str] = ..., feature_server_canary_follower_endpoint: _Optional[str] = ...) -> None: ...

class CacheParams(_message.Message):
    __slots__ = ["redis"]
    REDIS_FIELD_NUMBER: _ClassVar[int]
    redis: _feature_view__client_pb2_1.RedisOnlineStore
    def __init__(self, redis: _Optional[_Union[_feature_view__client_pb2_1.RedisOnlineStore, _Mapping]] = ...) -> None: ...

class FeatureServerConfiguration(_message.Message):
    __slots__ = ["computed_time", "feature_services", "global_table_config_by_name", "authorized_api_keys", "feature_service_acls", "workspace_acls", "all_online_store_params", "feature_server_canary_config", "remote_compute_configs", "all_online_compute_configs", "cache_groups", "cache_connection_configurations", "user_defined_function_map", "jwks", "transform_service_address"]
    class GlobalTableConfigByNameEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: GlobalTableConfig
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[GlobalTableConfig, _Mapping]] = ...) -> None: ...
    class CacheGroupsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: CacheGroup
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[CacheGroup, _Mapping]] = ...) -> None: ...
    class CacheConnectionConfigurationsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: CacheConnectionConfiguration
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[CacheConnectionConfiguration, _Mapping]] = ...) -> None: ...
    class UserDefinedFunctionMapEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _user_defined_function__client_pb2.UserDefinedFunction
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_user_defined_function__client_pb2.UserDefinedFunction, _Mapping]] = ...) -> None: ...
    class JwksEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: Jwk
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[Jwk, _Mapping]] = ...) -> None: ...
    COMPUTED_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICES_FIELD_NUMBER: _ClassVar[int]
    GLOBAL_TABLE_CONFIG_BY_NAME_FIELD_NUMBER: _ClassVar[int]
    AUTHORIZED_API_KEYS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_ACLS_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_ACLS_FIELD_NUMBER: _ClassVar[int]
    ALL_ONLINE_STORE_PARAMS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVER_CANARY_CONFIG_FIELD_NUMBER: _ClassVar[int]
    REMOTE_COMPUTE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    ALL_ONLINE_COMPUTE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    CACHE_GROUPS_FIELD_NUMBER: _ClassVar[int]
    CACHE_CONNECTION_CONFIGURATIONS_FIELD_NUMBER: _ClassVar[int]
    USER_DEFINED_FUNCTION_MAP_FIELD_NUMBER: _ClassVar[int]
    JWKS_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_SERVICE_ADDRESS_FIELD_NUMBER: _ClassVar[int]
    computed_time: _timestamp_pb2.Timestamp
    feature_services: _containers.RepeatedCompositeFieldContainer[FeatureServicePlan]
    global_table_config_by_name: _containers.MessageMap[str, GlobalTableConfig]
    authorized_api_keys: _containers.RepeatedCompositeFieldContainer[_tecton_api_key__client_pb2.TectonApiKey]
    feature_service_acls: _containers.RepeatedCompositeFieldContainer[FeatureServiceAcls]
    workspace_acls: _containers.RepeatedCompositeFieldContainer[WorkspaceAcls]
    all_online_store_params: _containers.RepeatedCompositeFieldContainer[_feature_view__client_pb2_1.OnlineStoreParams]
    feature_server_canary_config: CanaryConfig
    remote_compute_configs: _containers.RepeatedCompositeFieldContainer[_realtime_compute__client_pb2.RemoteFunctionComputeConfig]
    all_online_compute_configs: _containers.RepeatedCompositeFieldContainer[_realtime_compute__client_pb2.OnlineComputeConfig]
    cache_groups: _containers.MessageMap[str, CacheGroup]
    cache_connection_configurations: _containers.MessageMap[str, CacheConnectionConfiguration]
    user_defined_function_map: _containers.MessageMap[str, _user_defined_function__client_pb2.UserDefinedFunction]
    jwks: _containers.MessageMap[str, Jwk]
    transform_service_address: str
    def __init__(self, computed_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_services: _Optional[_Iterable[_Union[FeatureServicePlan, _Mapping]]] = ..., global_table_config_by_name: _Optional[_Mapping[str, GlobalTableConfig]] = ..., authorized_api_keys: _Optional[_Iterable[_Union[_tecton_api_key__client_pb2.TectonApiKey, _Mapping]]] = ..., feature_service_acls: _Optional[_Iterable[_Union[FeatureServiceAcls, _Mapping]]] = ..., workspace_acls: _Optional[_Iterable[_Union[WorkspaceAcls, _Mapping]]] = ..., all_online_store_params: _Optional[_Iterable[_Union[_feature_view__client_pb2_1.OnlineStoreParams, _Mapping]]] = ..., feature_server_canary_config: _Optional[_Union[CanaryConfig, _Mapping]] = ..., remote_compute_configs: _Optional[_Iterable[_Union[_realtime_compute__client_pb2.RemoteFunctionComputeConfig, _Mapping]]] = ..., all_online_compute_configs: _Optional[_Iterable[_Union[_realtime_compute__client_pb2.OnlineComputeConfig, _Mapping]]] = ..., cache_groups: _Optional[_Mapping[str, CacheGroup]] = ..., cache_connection_configurations: _Optional[_Mapping[str, CacheConnectionConfiguration]] = ..., user_defined_function_map: _Optional[_Mapping[str, _user_defined_function__client_pb2.UserDefinedFunction]] = ..., jwks: _Optional[_Mapping[str, Jwk]] = ..., transform_service_address: _Optional[str] = ...) -> None: ...

class CacheConnectionConfiguration(_message.Message):
    __slots__ = ["workspace_name", "cache_name", "elasticache_valkey"]
    class ElasticacheValkey(_message.Message):
        __slots__ = ["primary_endpoint", "aws_sm_key"]
        PRIMARY_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
        AWS_SM_KEY_FIELD_NUMBER: _ClassVar[int]
        primary_endpoint: str
        aws_sm_key: str
        def __init__(self, primary_endpoint: _Optional[str] = ..., aws_sm_key: _Optional[str] = ...) -> None: ...
    WORKSPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    CACHE_NAME_FIELD_NUMBER: _ClassVar[int]
    ELASTICACHE_VALKEY_FIELD_NUMBER: _ClassVar[int]
    workspace_name: str
    cache_name: str
    elasticache_valkey: CacheConnectionConfiguration.ElasticacheValkey
    def __init__(self, workspace_name: _Optional[str] = ..., cache_name: _Optional[str] = ..., elasticache_valkey: _Optional[_Union[CacheConnectionConfiguration.ElasticacheValkey, _Mapping]] = ...) -> None: ...

class Jwk(_message.Message):
    __slots__ = ["n", "alg", "use", "e"]
    N_FIELD_NUMBER: _ClassVar[int]
    ALG_FIELD_NUMBER: _ClassVar[int]
    USE_FIELD_NUMBER: _ClassVar[int]
    E_FIELD_NUMBER: _ClassVar[int]
    n: str
    alg: str
    use: str
    e: str
    def __init__(self, n: _Optional[str] = ..., alg: _Optional[str] = ..., use: _Optional[str] = ..., e: _Optional[str] = ...) -> None: ...

class RemappedJoinKeys(_message.Message):
    __slots__ = ["join_keys"]
    JOIN_KEYS_FIELD_NUMBER: _ClassVar[int]
    join_keys: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, join_keys: _Optional[_Iterable[str]] = ...) -> None: ...

class FeatureServiceCachePlan(_message.Message):
    __slots__ = ["feature_view_ids", "cache_group_name", "remapped_join_key_lists", "feature_set_column_hashes"]
    FEATURE_VIEW_IDS_FIELD_NUMBER: _ClassVar[int]
    CACHE_GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    REMAPPED_JOIN_KEY_LISTS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SET_COLUMN_HASHES_FIELD_NUMBER: _ClassVar[int]
    feature_view_ids: _containers.RepeatedScalarFieldContainer[str]
    cache_group_name: str
    remapped_join_key_lists: _containers.RepeatedCompositeFieldContainer[RemappedJoinKeys]
    feature_set_column_hashes: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, feature_view_ids: _Optional[_Iterable[str]] = ..., cache_group_name: _Optional[str] = ..., remapped_join_key_lists: _Optional[_Iterable[_Union[RemappedJoinKeys, _Mapping]]] = ..., feature_set_column_hashes: _Optional[_Iterable[str]] = ...) -> None: ...

class CacheGroup(_message.Message):
    __slots__ = ["name", "join_keys", "key_ttl", "key_jitter", "feature_view_ids"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    JOIN_KEYS_FIELD_NUMBER: _ClassVar[int]
    KEY_TTL_FIELD_NUMBER: _ClassVar[int]
    KEY_JITTER_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_IDS_FIELD_NUMBER: _ClassVar[int]
    name: str
    join_keys: _containers.RepeatedScalarFieldContainer[str]
    key_ttl: _duration_pb2.Duration
    key_jitter: _duration_pb2.Duration
    feature_view_ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, name: _Optional[str] = ..., join_keys: _Optional[_Iterable[str]] = ..., key_ttl: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., key_jitter: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., feature_view_ids: _Optional[_Iterable[str]] = ...) -> None: ...
