from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.args import basic_info__client_pb2 as _basic_info__client_pb2
from tecton_proto.args import data_source__client_pb2 as _data_source__client_pb2
from tecton_proto.args import diff_options__client_pb2 as _diff_options__client_pb2
from tecton_proto.args import pipeline__client_pb2 as _pipeline__client_pb2
from tecton_proto.args import transformation__client_pb2 as _transformation__client_pb2
from tecton_proto.args import user_defined_function__client_pb2 as _user_defined_function__client_pb2
from tecton_proto.common import analytics_options__client_pb2 as _analytics_options__client_pb2
from tecton_proto.common import calculation_node__client_pb2 as _calculation_node__client_pb2
from tecton_proto.common import compute_identity__client_pb2 as _compute_identity__client_pb2
from tecton_proto.common import compute_mode__client_pb2 as _compute_mode__client_pb2
from tecton_proto.common import data_source_type__client_pb2 as _data_source_type__client_pb2
from tecton_proto.common import data_type__client_pb2 as _data_type__client_pb2
from tecton_proto.common import framework_version__client_pb2 as _framework_version__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import python_version__client_pb2 as _python_version__client_pb2
from tecton_proto.common import schema__client_pb2 as _schema__client_pb2
from tecton_proto.common import secret__client_pb2 as _secret__client_pb2
from tecton_proto.common import spark_schema__client_pb2 as _spark_schema__client_pb2
from tecton_proto.common import time_window__client_pb2 as _time_window__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FeatureViewType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    FEATURE_VIEW_TYPE_UNSPECIFIED: _ClassVar[FeatureViewType]
    FEATURE_VIEW_TYPE_REALTIME: _ClassVar[FeatureViewType]
    FEATURE_VIEW_TYPE_FEATURE_TABLE: _ClassVar[FeatureViewType]
    FEATURE_VIEW_TYPE_FWV5_FEATURE_VIEW: _ClassVar[FeatureViewType]
    FEATURE_VIEW_TYPE_PROMPT: _ClassVar[FeatureViewType]

class BackfillConfigMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    BACKFILL_CONFIG_MODE_UNSPECIFIED: _ClassVar[BackfillConfigMode]
    BACKFILL_CONFIG_MODE_SINGLE_BATCH_SCHEDULE_INTERVAL_PER_JOB: _ClassVar[BackfillConfigMode]
    BACKFILL_CONFIG_MODE_MULTIPLE_BATCH_SCHEDULE_INTERVALS_PER_JOB: _ClassVar[BackfillConfigMode]

class AggregationLeadingEdge(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    AGGREGATION_MODE_UNSPECIFIED: _ClassVar[AggregationLeadingEdge]
    AGGREGATION_MODE_WALL_CLOCK_TIME: _ClassVar[AggregationLeadingEdge]
    AGGREGATION_MODE_LATEST_EVENT_TIME: _ClassVar[AggregationLeadingEdge]

class StreamProcessingMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    STREAM_PROCESSING_MODE_UNSPECIFIED: _ClassVar[StreamProcessingMode]
    STREAM_PROCESSING_MODE_TIME_INTERVAL: _ClassVar[StreamProcessingMode]
    STREAM_PROCESSING_MODE_CONTINUOUS: _ClassVar[StreamProcessingMode]

class BatchTriggerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    BATCH_TRIGGER_TYPE_UNSPECIFIED: _ClassVar[BatchTriggerType]
    BATCH_TRIGGER_TYPE_SCHEDULED: _ClassVar[BatchTriggerType]
    BATCH_TRIGGER_TYPE_MANUAL: _ClassVar[BatchTriggerType]
    BATCH_TRIGGER_TYPE_NO_BATCH_MATERIALIZATION: _ClassVar[BatchTriggerType]

class FeatureStoreFormatVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    FEATURE_STORE_FORMAT_VERSION_DEFAULT: _ClassVar[FeatureStoreFormatVersion]
    FEATURE_STORE_FORMAT_VERSION_TIME_NANOSECONDS: _ClassVar[FeatureStoreFormatVersion]
    FEATURE_STORE_FORMAT_VERSION_TTL_FIELD: _ClassVar[FeatureStoreFormatVersion]
    FEATURE_STORE_FORMAT_VERSION_MAX: _ClassVar[FeatureStoreFormatVersion]
    FEATURE_STORE_FORMAT_VERSION_ONLINE_STORE_TTL_DELETION_ENABLED: _ClassVar[FeatureStoreFormatVersion]
FEATURE_VIEW_TYPE_UNSPECIFIED: FeatureViewType
FEATURE_VIEW_TYPE_REALTIME: FeatureViewType
FEATURE_VIEW_TYPE_FEATURE_TABLE: FeatureViewType
FEATURE_VIEW_TYPE_FWV5_FEATURE_VIEW: FeatureViewType
FEATURE_VIEW_TYPE_PROMPT: FeatureViewType
BACKFILL_CONFIG_MODE_UNSPECIFIED: BackfillConfigMode
BACKFILL_CONFIG_MODE_SINGLE_BATCH_SCHEDULE_INTERVAL_PER_JOB: BackfillConfigMode
BACKFILL_CONFIG_MODE_MULTIPLE_BATCH_SCHEDULE_INTERVALS_PER_JOB: BackfillConfigMode
AGGREGATION_MODE_UNSPECIFIED: AggregationLeadingEdge
AGGREGATION_MODE_WALL_CLOCK_TIME: AggregationLeadingEdge
AGGREGATION_MODE_LATEST_EVENT_TIME: AggregationLeadingEdge
STREAM_PROCESSING_MODE_UNSPECIFIED: StreamProcessingMode
STREAM_PROCESSING_MODE_TIME_INTERVAL: StreamProcessingMode
STREAM_PROCESSING_MODE_CONTINUOUS: StreamProcessingMode
BATCH_TRIGGER_TYPE_UNSPECIFIED: BatchTriggerType
BATCH_TRIGGER_TYPE_SCHEDULED: BatchTriggerType
BATCH_TRIGGER_TYPE_MANUAL: BatchTriggerType
BATCH_TRIGGER_TYPE_NO_BATCH_MATERIALIZATION: BatchTriggerType
FEATURE_STORE_FORMAT_VERSION_DEFAULT: FeatureStoreFormatVersion
FEATURE_STORE_FORMAT_VERSION_TIME_NANOSECONDS: FeatureStoreFormatVersion
FEATURE_STORE_FORMAT_VERSION_TTL_FIELD: FeatureStoreFormatVersion
FEATURE_STORE_FORMAT_VERSION_MAX: FeatureStoreFormatVersion
FEATURE_STORE_FORMAT_VERSION_ONLINE_STORE_TTL_DELETION_ENABLED: FeatureStoreFormatVersion

class FeatureViewArgs(_message.Message):
    __slots__ = ["feature_view_id", "feature_view_type", "info", "version", "prevent_destroy", "options", "cache_config", "entities", "resource_providers", "materialized_feature_view_args", "realtime_args", "feature_table_args", "prompt_args", "context_parameter_name", "secrets", "online_serving_index", "online_enabled", "offline_enabled", "batch_compute_mode", "pipeline", "data_quality_config", "forced_view_schema", "forced_materialized_schema"]
    class OptionsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class ResourceProvidersEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _id__client_pb2.Id
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ...) -> None: ...
    class SecretsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _secret__client_pb2.SecretReference
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_secret__client_pb2.SecretReference, _Mapping]] = ...) -> None: ...
    FEATURE_VIEW_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_TYPE_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    PREVENT_DESTROY_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    CACHE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_PROVIDERS_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZED_FEATURE_VIEW_ARGS_FIELD_NUMBER: _ClassVar[int]
    REALTIME_ARGS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_TABLE_ARGS_FIELD_NUMBER: _ClassVar[int]
    PROMPT_ARGS_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_PARAMETER_NAME_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    ONLINE_SERVING_INDEX_FIELD_NUMBER: _ClassVar[int]
    ONLINE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    BATCH_COMPUTE_MODE_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_FIELD_NUMBER: _ClassVar[int]
    DATA_QUALITY_CONFIG_FIELD_NUMBER: _ClassVar[int]
    FORCED_VIEW_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    FORCED_MATERIALIZED_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    feature_view_id: _id__client_pb2.Id
    feature_view_type: FeatureViewType
    info: _basic_info__client_pb2.BasicInfo
    version: _framework_version__client_pb2.FrameworkVersion
    prevent_destroy: bool
    options: _containers.ScalarMap[str, str]
    cache_config: CacheConfig
    entities: _containers.RepeatedCompositeFieldContainer[EntityKeyOverride]
    resource_providers: _containers.MessageMap[str, _id__client_pb2.Id]
    materialized_feature_view_args: MaterializedFeatureViewArgs
    realtime_args: RealtimeArgs
    feature_table_args: FeatureTableArgs
    prompt_args: PromptArgs
    context_parameter_name: str
    secrets: _containers.MessageMap[str, _secret__client_pb2.SecretReference]
    online_serving_index: _containers.RepeatedScalarFieldContainer[str]
    online_enabled: bool
    offline_enabled: bool
    batch_compute_mode: _compute_mode__client_pb2.BatchComputeMode
    pipeline: _pipeline__client_pb2.Pipeline
    data_quality_config: DataQualityConfig
    forced_view_schema: _spark_schema__client_pb2.SparkSchema
    forced_materialized_schema: _spark_schema__client_pb2.SparkSchema
    def __init__(self, feature_view_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., feature_view_type: _Optional[_Union[FeatureViewType, str]] = ..., info: _Optional[_Union[_basic_info__client_pb2.BasicInfo, _Mapping]] = ..., version: _Optional[_Union[_framework_version__client_pb2.FrameworkVersion, str]] = ..., prevent_destroy: bool = ..., options: _Optional[_Mapping[str, str]] = ..., cache_config: _Optional[_Union[CacheConfig, _Mapping]] = ..., entities: _Optional[_Iterable[_Union[EntityKeyOverride, _Mapping]]] = ..., resource_providers: _Optional[_Mapping[str, _id__client_pb2.Id]] = ..., materialized_feature_view_args: _Optional[_Union[MaterializedFeatureViewArgs, _Mapping]] = ..., realtime_args: _Optional[_Union[RealtimeArgs, _Mapping]] = ..., feature_table_args: _Optional[_Union[FeatureTableArgs, _Mapping]] = ..., prompt_args: _Optional[_Union[PromptArgs, _Mapping]] = ..., context_parameter_name: _Optional[str] = ..., secrets: _Optional[_Mapping[str, _secret__client_pb2.SecretReference]] = ..., online_serving_index: _Optional[_Iterable[str]] = ..., online_enabled: bool = ..., offline_enabled: bool = ..., batch_compute_mode: _Optional[_Union[_compute_mode__client_pb2.BatchComputeMode, str]] = ..., pipeline: _Optional[_Union[_pipeline__client_pb2.Pipeline, _Mapping]] = ..., data_quality_config: _Optional[_Union[DataQualityConfig, _Mapping]] = ..., forced_view_schema: _Optional[_Union[_spark_schema__client_pb2.SparkSchema, _Mapping]] = ..., forced_materialized_schema: _Optional[_Union[_spark_schema__client_pb2.SparkSchema, _Mapping]] = ...) -> None: ...

class EntityKeyOverride(_message.Message):
    __slots__ = ["entity_id", "join_keys"]
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    JOIN_KEYS_FIELD_NUMBER: _ClassVar[int]
    entity_id: _id__client_pb2.Id
    join_keys: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, entity_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., join_keys: _Optional[_Iterable[str]] = ...) -> None: ...

class BackfillConfig(_message.Message):
    __slots__ = ["mode"]
    MODE_FIELD_NUMBER: _ClassVar[int]
    mode: BackfillConfigMode
    def __init__(self, mode: _Optional[_Union[BackfillConfigMode, str]] = ...) -> None: ...

class OutputStream(_message.Message):
    __slots__ = ["include_features", "kinesis", "kafka"]
    INCLUDE_FEATURES_FIELD_NUMBER: _ClassVar[int]
    KINESIS_FIELD_NUMBER: _ClassVar[int]
    KAFKA_FIELD_NUMBER: _ClassVar[int]
    include_features: bool
    kinesis: _data_source__client_pb2.KinesisDataSourceArgs
    kafka: _data_source__client_pb2.KafkaDataSourceArgs
    def __init__(self, include_features: bool = ..., kinesis: _Optional[_Union[_data_source__client_pb2.KinesisDataSourceArgs, _Mapping]] = ..., kafka: _Optional[_Union[_data_source__client_pb2.KafkaDataSourceArgs, _Mapping]] = ...) -> None: ...

class SinkConfig(_message.Message):
    __slots__ = ["name", "function", "secrets", "mode"]
    class SecretsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _secret__client_pb2.SecretReference
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_secret__client_pb2.SecretReference, _Mapping]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    name: str
    function: _user_defined_function__client_pb2.UserDefinedFunction
    secrets: _containers.MessageMap[str, _secret__client_pb2.SecretReference]
    mode: _transformation__client_pb2.TransformationMode
    def __init__(self, name: _Optional[str] = ..., function: _Optional[_Union[_user_defined_function__client_pb2.UserDefinedFunction, _Mapping]] = ..., secrets: _Optional[_Mapping[str, _secret__client_pb2.SecretReference]] = ..., mode: _Optional[_Union[_transformation__client_pb2.TransformationMode, str]] = ...) -> None: ...

class DataLakeConfig(_message.Message):
    __slots__ = ["delta"]
    DELTA_FIELD_NUMBER: _ClassVar[int]
    delta: DeltaConfig
    def __init__(self, delta: _Optional[_Union[DeltaConfig, _Mapping]] = ...) -> None: ...

class PublishFeaturesConfig(_message.Message):
    __slots__ = ["publish_start_time", "sink_config", "data_lake_config"]
    PUBLISH_START_TIME_FIELD_NUMBER: _ClassVar[int]
    SINK_CONFIG_FIELD_NUMBER: _ClassVar[int]
    DATA_LAKE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    publish_start_time: _timestamp_pb2.Timestamp
    sink_config: SinkConfig
    data_lake_config: DataLakeConfig
    def __init__(self, publish_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., sink_config: _Optional[_Union[SinkConfig, _Mapping]] = ..., data_lake_config: _Optional[_Union[DataLakeConfig, _Mapping]] = ...) -> None: ...

class MaterializedFeatureViewArgs(_message.Message):
    __slots__ = ["timestamp_field", "batch_schedule", "feature_start_time", "manual_trigger_backfill_end_time", "max_backfill_interval", "serving_ttl", "offline_store_legacy", "offline_store", "publish_features_configs", "batch_compute", "stream_compute", "monitoring", "data_source_type", "online_store", "incremental_backfills", "aggregation_interval", "stream_processing_mode", "aggregations", "output_stream", "batch_trigger", "schema", "aggregation_secondary_key", "secondary_key_output_columns", "run_transformation_validation", "tecton_materialization_runtime", "lifetime_start_time", "compaction_enabled", "stream_tiling_enabled", "stream_tile_size", "environment", "transform_server_group", "attributes", "embeddings", "inferences", "aggregation_leading_edge", "feature_store_format_version", "secrets", "batch_publish_timestamp"]
    class SecretsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _secret__client_pb2.SecretReference
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_secret__client_pb2.SecretReference, _Mapping]] = ...) -> None: ...
    TIMESTAMP_FIELD_FIELD_NUMBER: _ClassVar[int]
    BATCH_SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_START_TIME_FIELD_NUMBER: _ClassVar[int]
    MANUAL_TRIGGER_BACKFILL_END_TIME_FIELD_NUMBER: _ClassVar[int]
    MAX_BACKFILL_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    SERVING_TTL_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_STORE_LEGACY_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_STORE_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_FEATURES_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    BATCH_COMPUTE_FIELD_NUMBER: _ClassVar[int]
    STREAM_COMPUTE_FIELD_NUMBER: _ClassVar[int]
    MONITORING_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ONLINE_STORE_FIELD_NUMBER: _ClassVar[int]
    INCREMENTAL_BACKFILLS_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    STREAM_PROCESSING_MODE_FIELD_NUMBER: _ClassVar[int]
    AGGREGATIONS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_STREAM_FIELD_NUMBER: _ClassVar[int]
    BATCH_TRIGGER_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_SECONDARY_KEY_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_KEY_OUTPUT_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    RUN_TRANSFORMATION_VALIDATION_FIELD_NUMBER: _ClassVar[int]
    TECTON_MATERIALIZATION_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    LIFETIME_START_TIME_FIELD_NUMBER: _ClassVar[int]
    COMPACTION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    STREAM_TILING_ENABLED_FIELD_NUMBER: _ClassVar[int]
    STREAM_TILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_SERVER_GROUP_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    INFERENCES_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_LEADING_EDGE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_STORE_FORMAT_VERSION_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    BATCH_PUBLISH_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    timestamp_field: str
    batch_schedule: _duration_pb2.Duration
    feature_start_time: _timestamp_pb2.Timestamp
    manual_trigger_backfill_end_time: _timestamp_pb2.Timestamp
    max_backfill_interval: _duration_pb2.Duration
    serving_ttl: _duration_pb2.Duration
    offline_store_legacy: OfflineFeatureStoreConfig
    offline_store: OfflineStoreConfig
    publish_features_configs: _containers.RepeatedCompositeFieldContainer[PublishFeaturesConfig]
    batch_compute: ClusterConfig
    stream_compute: ClusterConfig
    monitoring: MonitoringConfig
    data_source_type: _data_source_type__client_pb2.DataSourceType
    online_store: OnlineStoreConfig
    incremental_backfills: bool
    aggregation_interval: _duration_pb2.Duration
    stream_processing_mode: StreamProcessingMode
    aggregations: _containers.RepeatedCompositeFieldContainer[FeatureAggregation]
    output_stream: OutputStream
    batch_trigger: BatchTriggerType
    schema: _schema__client_pb2.Schema
    aggregation_secondary_key: str
    secondary_key_output_columns: _containers.RepeatedCompositeFieldContainer[SecondaryKeyOutputColumn]
    run_transformation_validation: bool
    tecton_materialization_runtime: str
    lifetime_start_time: _timestamp_pb2.Timestamp
    compaction_enabled: bool
    stream_tiling_enabled: bool
    stream_tile_size: _duration_pb2.Duration
    environment: str
    transform_server_group: str
    attributes: _containers.RepeatedCompositeFieldContainer[Attribute]
    embeddings: _containers.RepeatedCompositeFieldContainer[Embedding]
    inferences: _containers.RepeatedCompositeFieldContainer[Inference]
    aggregation_leading_edge: AggregationLeadingEdge
    feature_store_format_version: FeatureStoreFormatVersion
    secrets: _containers.MessageMap[str, _secret__client_pb2.SecretReference]
    batch_publish_timestamp: str
    def __init__(self, timestamp_field: _Optional[str] = ..., batch_schedule: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., feature_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., manual_trigger_backfill_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., max_backfill_interval: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., serving_ttl: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., offline_store_legacy: _Optional[_Union[OfflineFeatureStoreConfig, _Mapping]] = ..., offline_store: _Optional[_Union[OfflineStoreConfig, _Mapping]] = ..., publish_features_configs: _Optional[_Iterable[_Union[PublishFeaturesConfig, _Mapping]]] = ..., batch_compute: _Optional[_Union[ClusterConfig, _Mapping]] = ..., stream_compute: _Optional[_Union[ClusterConfig, _Mapping]] = ..., monitoring: _Optional[_Union[MonitoringConfig, _Mapping]] = ..., data_source_type: _Optional[_Union[_data_source_type__client_pb2.DataSourceType, str]] = ..., online_store: _Optional[_Union[OnlineStoreConfig, _Mapping]] = ..., incremental_backfills: bool = ..., aggregation_interval: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., stream_processing_mode: _Optional[_Union[StreamProcessingMode, str]] = ..., aggregations: _Optional[_Iterable[_Union[FeatureAggregation, _Mapping]]] = ..., output_stream: _Optional[_Union[OutputStream, _Mapping]] = ..., batch_trigger: _Optional[_Union[BatchTriggerType, str]] = ..., schema: _Optional[_Union[_schema__client_pb2.Schema, _Mapping]] = ..., aggregation_secondary_key: _Optional[str] = ..., secondary_key_output_columns: _Optional[_Iterable[_Union[SecondaryKeyOutputColumn, _Mapping]]] = ..., run_transformation_validation: bool = ..., tecton_materialization_runtime: _Optional[str] = ..., lifetime_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., compaction_enabled: bool = ..., stream_tiling_enabled: bool = ..., stream_tile_size: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., environment: _Optional[str] = ..., transform_server_group: _Optional[str] = ..., attributes: _Optional[_Iterable[_Union[Attribute, _Mapping]]] = ..., embeddings: _Optional[_Iterable[_Union[Embedding, _Mapping]]] = ..., inferences: _Optional[_Iterable[_Union[Inference, _Mapping]]] = ..., aggregation_leading_edge: _Optional[_Union[AggregationLeadingEdge, str]] = ..., feature_store_format_version: _Optional[_Union[FeatureStoreFormatVersion, str]] = ..., secrets: _Optional[_Mapping[str, _secret__client_pb2.SecretReference]] = ..., batch_publish_timestamp: _Optional[str] = ...) -> None: ...

class Attribute(_message.Message):
    __slots__ = ["name", "column_dtype", "description", "tags"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    COLUMN_DTYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    name: str
    column_dtype: _data_type__client_pb2.DataType
    description: str
    tags: _containers.ScalarMap[str, str]
    def __init__(self, name: _Optional[str] = ..., column_dtype: _Optional[_Union[_data_type__client_pb2.DataType, _Mapping]] = ..., description: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Calculation(_message.Message):
    __slots__ = ["name", "expr", "column_dtype", "description", "tags", "abstract_syntax_tree_root"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    EXPR_FIELD_NUMBER: _ClassVar[int]
    COLUMN_DTYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    ABSTRACT_SYNTAX_TREE_ROOT_FIELD_NUMBER: _ClassVar[int]
    name: str
    expr: str
    column_dtype: _data_type__client_pb2.DataType
    description: str
    tags: _containers.ScalarMap[str, str]
    abstract_syntax_tree_root: _calculation_node__client_pb2.AbstractSyntaxTreeNode
    def __init__(self, name: _Optional[str] = ..., expr: _Optional[str] = ..., column_dtype: _Optional[_Union[_data_type__client_pb2.DataType, _Mapping]] = ..., description: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ..., abstract_syntax_tree_root: _Optional[_Union[_calculation_node__client_pb2.AbstractSyntaxTreeNode, _Mapping]] = ...) -> None: ...

class Inference(_message.Message):
    __slots__ = ["input_columns", "name", "model", "description", "tags"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    INPUT_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    input_columns: _containers.RepeatedCompositeFieldContainer[_schema__client_pb2.Field]
    name: str
    model: str
    description: str
    tags: _containers.ScalarMap[str, str]
    def __init__(self, input_columns: _Optional[_Iterable[_Union[_schema__client_pb2.Field, _Mapping]]] = ..., name: _Optional[str] = ..., model: _Optional[str] = ..., description: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Embedding(_message.Message):
    __slots__ = ["name", "column", "column_dtype", "model", "description", "tags"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    COLUMN_DTYPE_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    name: str
    column: str
    column_dtype: _data_type__client_pb2.DataType
    model: str
    description: str
    tags: _containers.ScalarMap[str, str]
    def __init__(self, name: _Optional[str] = ..., column: _Optional[str] = ..., column_dtype: _Optional[_Union[_data_type__client_pb2.DataType, _Mapping]] = ..., model: _Optional[str] = ..., description: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class PromptArgs(_message.Message):
    __slots__ = ["environment", "attributes"]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    environment: str
    attributes: _containers.RepeatedCompositeFieldContainer[Attribute]
    def __init__(self, environment: _Optional[str] = ..., attributes: _Optional[_Iterable[_Union[Attribute, _Mapping]]] = ...) -> None: ...

class RealtimeArgs(_message.Message):
    __slots__ = ["schema", "environments", "required_packages", "attributes", "calculations"]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENTS_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_PACKAGES_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    CALCULATIONS_FIELD_NUMBER: _ClassVar[int]
    schema: _spark_schema__client_pb2.SparkSchema
    environments: _containers.RepeatedScalarFieldContainer[str]
    required_packages: _containers.RepeatedScalarFieldContainer[str]
    attributes: _containers.RepeatedCompositeFieldContainer[Attribute]
    calculations: _containers.RepeatedCompositeFieldContainer[Calculation]
    def __init__(self, schema: _Optional[_Union[_spark_schema__client_pb2.SparkSchema, _Mapping]] = ..., environments: _Optional[_Iterable[str]] = ..., required_packages: _Optional[_Iterable[str]] = ..., attributes: _Optional[_Iterable[_Union[Attribute, _Mapping]]] = ..., calculations: _Optional[_Iterable[_Union[Calculation, _Mapping]]] = ...) -> None: ...

class FeatureTableArgs(_message.Message):
    __slots__ = ["schema", "serving_ttl", "offline_store_legacy", "offline_store", "online_store", "batch_compute", "monitoring", "tecton_materialization_runtime", "attributes", "timestamp_field"]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SERVING_TTL_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_STORE_LEGACY_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_STORE_FIELD_NUMBER: _ClassVar[int]
    ONLINE_STORE_FIELD_NUMBER: _ClassVar[int]
    BATCH_COMPUTE_FIELD_NUMBER: _ClassVar[int]
    MONITORING_FIELD_NUMBER: _ClassVar[int]
    TECTON_MATERIALIZATION_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_FIELD_NUMBER: _ClassVar[int]
    schema: _spark_schema__client_pb2.SparkSchema
    serving_ttl: _duration_pb2.Duration
    offline_store_legacy: OfflineFeatureStoreConfig
    offline_store: OfflineStoreConfig
    online_store: OnlineStoreConfig
    batch_compute: ClusterConfig
    monitoring: MonitoringConfig
    tecton_materialization_runtime: str
    attributes: _containers.RepeatedCompositeFieldContainer[Attribute]
    timestamp_field: str
    def __init__(self, schema: _Optional[_Union[_spark_schema__client_pb2.SparkSchema, _Mapping]] = ..., serving_ttl: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., offline_store_legacy: _Optional[_Union[OfflineFeatureStoreConfig, _Mapping]] = ..., offline_store: _Optional[_Union[OfflineStoreConfig, _Mapping]] = ..., online_store: _Optional[_Union[OnlineStoreConfig, _Mapping]] = ..., batch_compute: _Optional[_Union[ClusterConfig, _Mapping]] = ..., monitoring: _Optional[_Union[MonitoringConfig, _Mapping]] = ..., tecton_materialization_runtime: _Optional[str] = ..., attributes: _Optional[_Iterable[_Union[Attribute, _Mapping]]] = ..., timestamp_field: _Optional[str] = ...) -> None: ...

class FeatureAggregation(_message.Message):
    __slots__ = ["column", "function", "function_params", "time_window_legacy", "name", "time_window", "lifetime_window", "time_window_series", "column_dtype", "batch_sawtooth_tile_size", "description", "tags"]
    class FunctionParamsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ParamValue
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ParamValue, _Mapping]] = ...) -> None: ...
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_PARAMS_FIELD_NUMBER: _ClassVar[int]
    TIME_WINDOW_LEGACY_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TIME_WINDOW_FIELD_NUMBER: _ClassVar[int]
    LIFETIME_WINDOW_FIELD_NUMBER: _ClassVar[int]
    TIME_WINDOW_SERIES_FIELD_NUMBER: _ClassVar[int]
    COLUMN_DTYPE_FIELD_NUMBER: _ClassVar[int]
    BATCH_SAWTOOTH_TILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    column: str
    function: str
    function_params: _containers.MessageMap[str, ParamValue]
    time_window_legacy: _duration_pb2.Duration
    name: str
    time_window: TimeWindow
    lifetime_window: _time_window__client_pb2.LifetimeWindow
    time_window_series: TimeWindowSeries
    column_dtype: _data_type__client_pb2.DataType
    batch_sawtooth_tile_size: _duration_pb2.Duration
    description: str
    tags: _containers.ScalarMap[str, str]
    def __init__(self, column: _Optional[str] = ..., function: _Optional[str] = ..., function_params: _Optional[_Mapping[str, ParamValue]] = ..., time_window_legacy: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., name: _Optional[str] = ..., time_window: _Optional[_Union[TimeWindow, _Mapping]] = ..., lifetime_window: _Optional[_Union[_time_window__client_pb2.LifetimeWindow, _Mapping]] = ..., time_window_series: _Optional[_Union[TimeWindowSeries, _Mapping]] = ..., column_dtype: _Optional[_Union[_data_type__client_pb2.DataType, _Mapping]] = ..., batch_sawtooth_tile_size: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., description: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ParamValue(_message.Message):
    __slots__ = ["int64_value", "double_value"]
    INT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    DOUBLE_VALUE_FIELD_NUMBER: _ClassVar[int]
    int64_value: int
    double_value: float
    def __init__(self, int64_value: _Optional[int] = ..., double_value: _Optional[float] = ...) -> None: ...

class DataQualityConfig(_message.Message):
    __slots__ = ["data_quality_enabled", "skip_default_expectations"]
    DATA_QUALITY_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SKIP_DEFAULT_EXPECTATIONS_FIELD_NUMBER: _ClassVar[int]
    data_quality_enabled: bool
    skip_default_expectations: bool
    def __init__(self, data_quality_enabled: bool = ..., skip_default_expectations: bool = ...) -> None: ...

class ClusterConfig(_message.Message):
    __slots__ = ["existing_cluster", "new_databricks", "new_emr", "implicit_config", "json_databricks", "json_emr", "json_dataproc", "rift", "compute_identity"]
    EXISTING_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    NEW_DATABRICKS_FIELD_NUMBER: _ClassVar[int]
    NEW_EMR_FIELD_NUMBER: _ClassVar[int]
    IMPLICIT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    JSON_DATABRICKS_FIELD_NUMBER: _ClassVar[int]
    JSON_EMR_FIELD_NUMBER: _ClassVar[int]
    JSON_DATAPROC_FIELD_NUMBER: _ClassVar[int]
    RIFT_FIELD_NUMBER: _ClassVar[int]
    COMPUTE_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    existing_cluster: ExistingClusterConfig
    new_databricks: NewClusterConfig
    new_emr: NewClusterConfig
    implicit_config: DefaultClusterConfig
    json_databricks: JsonClusterConfig
    json_emr: JsonClusterConfig
    json_dataproc: JsonClusterConfig
    rift: RiftClusterConfig
    compute_identity: _compute_identity__client_pb2.ComputeIdentity
    def __init__(self, existing_cluster: _Optional[_Union[ExistingClusterConfig, _Mapping]] = ..., new_databricks: _Optional[_Union[NewClusterConfig, _Mapping]] = ..., new_emr: _Optional[_Union[NewClusterConfig, _Mapping]] = ..., implicit_config: _Optional[_Union[DefaultClusterConfig, _Mapping]] = ..., json_databricks: _Optional[_Union[JsonClusterConfig, _Mapping]] = ..., json_emr: _Optional[_Union[JsonClusterConfig, _Mapping]] = ..., json_dataproc: _Optional[_Union[JsonClusterConfig, _Mapping]] = ..., rift: _Optional[_Union[RiftClusterConfig, _Mapping]] = ..., compute_identity: _Optional[_Union[_compute_identity__client_pb2.ComputeIdentity, _Mapping]] = ...) -> None: ...

class JsonClusterConfig(_message.Message):
    __slots__ = ["json"]
    JSON_FIELD_NUMBER: _ClassVar[int]
    json: _struct_pb2.Struct
    def __init__(self, json: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ...) -> None: ...

class ExistingClusterConfig(_message.Message):
    __slots__ = ["existing_cluster_id"]
    EXISTING_CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    existing_cluster_id: str
    def __init__(self, existing_cluster_id: _Optional[str] = ...) -> None: ...

class NewClusterConfig(_message.Message):
    __slots__ = ["instance_type", "instance_availability", "number_of_workers", "root_volume_size_in_gb", "extra_pip_dependencies", "spark_config", "first_on_demand", "pinned_spark_version", "python_version"]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_AVAILABILITY_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_WORKERS_FIELD_NUMBER: _ClassVar[int]
    ROOT_VOLUME_SIZE_IN_GB_FIELD_NUMBER: _ClassVar[int]
    EXTRA_PIP_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    SPARK_CONFIG_FIELD_NUMBER: _ClassVar[int]
    FIRST_ON_DEMAND_FIELD_NUMBER: _ClassVar[int]
    PINNED_SPARK_VERSION_FIELD_NUMBER: _ClassVar[int]
    PYTHON_VERSION_FIELD_NUMBER: _ClassVar[int]
    instance_type: str
    instance_availability: str
    number_of_workers: int
    root_volume_size_in_gb: int
    extra_pip_dependencies: _containers.RepeatedScalarFieldContainer[str]
    spark_config: SparkConfig
    first_on_demand: int
    pinned_spark_version: str
    python_version: _python_version__client_pb2.PythonVersion
    def __init__(self, instance_type: _Optional[str] = ..., instance_availability: _Optional[str] = ..., number_of_workers: _Optional[int] = ..., root_volume_size_in_gb: _Optional[int] = ..., extra_pip_dependencies: _Optional[_Iterable[str]] = ..., spark_config: _Optional[_Union[SparkConfig, _Mapping]] = ..., first_on_demand: _Optional[int] = ..., pinned_spark_version: _Optional[str] = ..., python_version: _Optional[_Union[_python_version__client_pb2.PythonVersion, str]] = ...) -> None: ...

class RiftClusterConfig(_message.Message):
    __slots__ = ["instance_type", "root_volume_size_in_gb"]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ROOT_VOLUME_SIZE_IN_GB_FIELD_NUMBER: _ClassVar[int]
    instance_type: str
    root_volume_size_in_gb: int
    def __init__(self, instance_type: _Optional[str] = ..., root_volume_size_in_gb: _Optional[int] = ...) -> None: ...

class DefaultClusterConfig(_message.Message):
    __slots__ = ["databricks_spark_version", "emr_spark_version", "tecton_compute_instance_type", "emr_python_version"]
    DATABRICKS_SPARK_VERSION_FIELD_NUMBER: _ClassVar[int]
    EMR_SPARK_VERSION_FIELD_NUMBER: _ClassVar[int]
    TECTON_COMPUTE_INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    EMR_PYTHON_VERSION_FIELD_NUMBER: _ClassVar[int]
    databricks_spark_version: str
    emr_spark_version: str
    tecton_compute_instance_type: str
    emr_python_version: _python_version__client_pb2.PythonVersion
    def __init__(self, databricks_spark_version: _Optional[str] = ..., emr_spark_version: _Optional[str] = ..., tecton_compute_instance_type: _Optional[str] = ..., emr_python_version: _Optional[_Union[_python_version__client_pb2.PythonVersion, str]] = ...) -> None: ...

class SparkConfig(_message.Message):
    __slots__ = ["spark_driver_memory", "spark_executor_memory", "spark_driver_memory_overhead", "spark_executor_memory_overhead", "spark_conf"]
    class SparkConfEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SPARK_DRIVER_MEMORY_FIELD_NUMBER: _ClassVar[int]
    SPARK_EXECUTOR_MEMORY_FIELD_NUMBER: _ClassVar[int]
    SPARK_DRIVER_MEMORY_OVERHEAD_FIELD_NUMBER: _ClassVar[int]
    SPARK_EXECUTOR_MEMORY_OVERHEAD_FIELD_NUMBER: _ClassVar[int]
    SPARK_CONF_FIELD_NUMBER: _ClassVar[int]
    spark_driver_memory: str
    spark_executor_memory: str
    spark_driver_memory_overhead: str
    spark_executor_memory_overhead: str
    spark_conf: _containers.ScalarMap[str, str]
    def __init__(self, spark_driver_memory: _Optional[str] = ..., spark_executor_memory: _Optional[str] = ..., spark_driver_memory_overhead: _Optional[str] = ..., spark_executor_memory_overhead: _Optional[str] = ..., spark_conf: _Optional[_Mapping[str, str]] = ...) -> None: ...

class OnlineStoreConfig(_message.Message):
    __slots__ = ["dynamo", "redis", "bigtable"]
    DYNAMO_FIELD_NUMBER: _ClassVar[int]
    REDIS_FIELD_NUMBER: _ClassVar[int]
    BIGTABLE_FIELD_NUMBER: _ClassVar[int]
    dynamo: DynamoDbOnlineStore
    redis: RedisOnlineStore
    bigtable: BigtableOnlineStore
    def __init__(self, dynamo: _Optional[_Union[DynamoDbOnlineStore, _Mapping]] = ..., redis: _Optional[_Union[RedisOnlineStore, _Mapping]] = ..., bigtable: _Optional[_Union[BigtableOnlineStore, _Mapping]] = ...) -> None: ...

class NullableStringList(_message.Message):
    __slots__ = ["values"]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, values: _Optional[_Iterable[str]] = ...) -> None: ...

class DynamoDbOnlineStore(_message.Message):
    __slots__ = ["enabled", "replica_regions"]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    REPLICA_REGIONS_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    replica_regions: NullableStringList
    def __init__(self, enabled: bool = ..., replica_regions: _Optional[_Union[NullableStringList, _Mapping]] = ...) -> None: ...

class RedisOnlineStore(_message.Message):
    __slots__ = ["primary_endpoint", "authentication_token", "enabled"]
    PRIMARY_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    AUTHENTICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    primary_endpoint: str
    authentication_token: str
    enabled: bool
    def __init__(self, primary_endpoint: _Optional[str] = ..., authentication_token: _Optional[str] = ..., enabled: bool = ...) -> None: ...

class BigtableOnlineStore(_message.Message):
    __slots__ = ["enabled", "project_id", "instance_id"]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    project_id: str
    instance_id: str
    def __init__(self, enabled: bool = ..., project_id: _Optional[str] = ..., instance_id: _Optional[str] = ...) -> None: ...

class OfflineFeatureStoreConfig(_message.Message):
    __slots__ = ["parquet", "delta", "iceberg", "subdirectory_override"]
    PARQUET_FIELD_NUMBER: _ClassVar[int]
    DELTA_FIELD_NUMBER: _ClassVar[int]
    ICEBERG_FIELD_NUMBER: _ClassVar[int]
    SUBDIRECTORY_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    parquet: ParquetConfig
    delta: DeltaConfig
    iceberg: IcebergConfig
    subdirectory_override: str
    def __init__(self, parquet: _Optional[_Union[ParquetConfig, _Mapping]] = ..., delta: _Optional[_Union[DeltaConfig, _Mapping]] = ..., iceberg: _Optional[_Union[IcebergConfig, _Mapping]] = ..., subdirectory_override: _Optional[str] = ...) -> None: ...

class ParquetConfig(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class DeltaConfig(_message.Message):
    __slots__ = ["time_partition_size"]
    TIME_PARTITION_SIZE_FIELD_NUMBER: _ClassVar[int]
    time_partition_size: _duration_pb2.Duration
    def __init__(self, time_partition_size: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class IcebergConfig(_message.Message):
    __slots__ = ["num_entity_buckets"]
    NUM_ENTITY_BUCKETS_FIELD_NUMBER: _ClassVar[int]
    num_entity_buckets: int
    def __init__(self, num_entity_buckets: _Optional[int] = ...) -> None: ...

class OfflineStoreConfig(_message.Message):
    __slots__ = ["staging_table_format", "publish_full_features", "publish_start_time"]
    STAGING_TABLE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_FULL_FEATURES_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_START_TIME_FIELD_NUMBER: _ClassVar[int]
    staging_table_format: OfflineFeatureStoreConfig
    publish_full_features: bool
    publish_start_time: _timestamp_pb2.Timestamp
    def __init__(self, staging_table_format: _Optional[_Union[OfflineFeatureStoreConfig, _Mapping]] = ..., publish_full_features: bool = ..., publish_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class MonitoringConfig(_message.Message):
    __slots__ = ["monitor_freshness", "expected_freshness", "alert_email"]
    MONITOR_FRESHNESS_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_FRESHNESS_FIELD_NUMBER: _ClassVar[int]
    ALERT_EMAIL_FIELD_NUMBER: _ClassVar[int]
    monitor_freshness: bool
    expected_freshness: _duration_pb2.Duration
    alert_email: str
    def __init__(self, monitor_freshness: bool = ..., expected_freshness: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., alert_email: _Optional[str] = ...) -> None: ...

class SecondaryKeyOutputColumn(_message.Message):
    __slots__ = ["time_window", "lifetime_window", "time_window_series", "name"]
    TIME_WINDOW_FIELD_NUMBER: _ClassVar[int]
    LIFETIME_WINDOW_FIELD_NUMBER: _ClassVar[int]
    TIME_WINDOW_SERIES_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    time_window: TimeWindow
    lifetime_window: _time_window__client_pb2.LifetimeWindow
    time_window_series: TimeWindowSeries
    name: str
    def __init__(self, time_window: _Optional[_Union[TimeWindow, _Mapping]] = ..., lifetime_window: _Optional[_Union[_time_window__client_pb2.LifetimeWindow, _Mapping]] = ..., time_window_series: _Optional[_Union[TimeWindowSeries, _Mapping]] = ..., name: _Optional[str] = ...) -> None: ...

class TimeWindow(_message.Message):
    __slots__ = ["window_duration", "offset"]
    WINDOW_DURATION_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    window_duration: _duration_pb2.Duration
    offset: _duration_pb2.Duration
    def __init__(self, window_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., offset: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class TimeWindowSeries(_message.Message):
    __slots__ = ["series_start", "series_end", "step_size", "window_duration"]
    SERIES_START_FIELD_NUMBER: _ClassVar[int]
    SERIES_END_FIELD_NUMBER: _ClassVar[int]
    STEP_SIZE_FIELD_NUMBER: _ClassVar[int]
    WINDOW_DURATION_FIELD_NUMBER: _ClassVar[int]
    series_start: _duration_pb2.Duration
    series_end: _duration_pb2.Duration
    step_size: _duration_pb2.Duration
    window_duration: _duration_pb2.Duration
    def __init__(self, series_start: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., series_end: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., step_size: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., window_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class CacheConfig(_message.Message):
    __slots__ = ["max_age_seconds"]
    MAX_AGE_SECONDS_FIELD_NUMBER: _ClassVar[int]
    max_age_seconds: int
    def __init__(self, max_age_seconds: _Optional[int] = ...) -> None: ...
