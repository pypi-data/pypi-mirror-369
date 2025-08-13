from google.protobuf import duration_pb2 as _duration_pb2
from tecton_proto.args import data_source_config__client_pb2 as _data_source_config__client_pb2
from tecton_proto.args import diff_options__client_pb2 as _diff_options__client_pb2
from tecton_proto.args import transformation__client_pb2 as _transformation__client_pb2
from tecton_proto.args import user_defined_function__client_pb2 as _user_defined_function__client_pb2
from tecton_proto.common import schema__client_pb2 as _schema__client_pb2
from tecton_proto.common import secret__client_pb2 as _secret__client_pb2
from tecton_proto.common import spark_schema__client_pb2 as _spark_schema__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UnityCatalogAccessMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNITY_CATALOG_ACCESS_MODE_UNSPECIFIED: _ClassVar[UnityCatalogAccessMode]
    UNITY_CATALOG_ACCESS_MODE_SINGLE_USER: _ClassVar[UnityCatalogAccessMode]
    UNITY_CATALOG_ACCESS_MODE_SINGLE_USER_WITH_FGAC: _ClassVar[UnityCatalogAccessMode]
    UNITY_CATALOG_ACCESS_MODE_SHARED: _ClassVar[UnityCatalogAccessMode]
UNITY_CATALOG_ACCESS_MODE_UNSPECIFIED: UnityCatalogAccessMode
UNITY_CATALOG_ACCESS_MODE_SINGLE_USER: UnityCatalogAccessMode
UNITY_CATALOG_ACCESS_MODE_SINGLE_USER_WITH_FGAC: UnityCatalogAccessMode
UNITY_CATALOG_ACCESS_MODE_SHARED: UnityCatalogAccessMode

class DatetimePartitionColumnArgs(_message.Message):
    __slots__ = ["column_name", "datepart", "zero_padded", "format_string"]
    COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    DATEPART_FIELD_NUMBER: _ClassVar[int]
    ZERO_PADDED_FIELD_NUMBER: _ClassVar[int]
    FORMAT_STRING_FIELD_NUMBER: _ClassVar[int]
    column_name: str
    datepart: str
    zero_padded: bool
    format_string: str
    def __init__(self, column_name: _Optional[str] = ..., datepart: _Optional[str] = ..., zero_padded: bool = ..., format_string: _Optional[str] = ...) -> None: ...

class BatchDataSourceCommonArgs(_message.Message):
    __slots__ = ["timestamp_field", "post_processor", "data_delay"]
    TIMESTAMP_FIELD_FIELD_NUMBER: _ClassVar[int]
    POST_PROCESSOR_FIELD_NUMBER: _ClassVar[int]
    DATA_DELAY_FIELD_NUMBER: _ClassVar[int]
    timestamp_field: str
    post_processor: _user_defined_function__client_pb2.UserDefinedFunction
    data_delay: _duration_pb2.Duration
    def __init__(self, timestamp_field: _Optional[str] = ..., post_processor: _Optional[_Union[_user_defined_function__client_pb2.UserDefinedFunction, _Mapping]] = ..., data_delay: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class StreamDataSourceCommonArgs(_message.Message):
    __slots__ = ["timestamp_field", "watermark_delay_threshold", "post_processor", "deduplication_columns"]
    TIMESTAMP_FIELD_FIELD_NUMBER: _ClassVar[int]
    WATERMARK_DELAY_THRESHOLD_FIELD_NUMBER: _ClassVar[int]
    POST_PROCESSOR_FIELD_NUMBER: _ClassVar[int]
    DEDUPLICATION_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    timestamp_field: str
    watermark_delay_threshold: _duration_pb2.Duration
    post_processor: _user_defined_function__client_pb2.UserDefinedFunction
    deduplication_columns: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, timestamp_field: _Optional[str] = ..., watermark_delay_threshold: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., post_processor: _Optional[_Union[_user_defined_function__client_pb2.UserDefinedFunction, _Mapping]] = ..., deduplication_columns: _Optional[_Iterable[str]] = ...) -> None: ...

class HiveDataSourceArgs(_message.Message):
    __slots__ = ["table", "database", "timestamp_format", "datetime_partition_columns", "common_args"]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FORMAT_FIELD_NUMBER: _ClassVar[int]
    DATETIME_PARTITION_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    COMMON_ARGS_FIELD_NUMBER: _ClassVar[int]
    table: str
    database: str
    timestamp_format: str
    datetime_partition_columns: _containers.RepeatedCompositeFieldContainer[DatetimePartitionColumnArgs]
    common_args: BatchDataSourceCommonArgs
    def __init__(self, table: _Optional[str] = ..., database: _Optional[str] = ..., timestamp_format: _Optional[str] = ..., datetime_partition_columns: _Optional[_Iterable[_Union[DatetimePartitionColumnArgs, _Mapping]]] = ..., common_args: _Optional[_Union[BatchDataSourceCommonArgs, _Mapping]] = ...) -> None: ...

class UnityDataSourceArgs(_message.Message):
    __slots__ = ["catalog", "schema", "table", "common_args", "timestamp_format", "datetime_partition_columns", "access_mode"]
    CATALOG_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    COMMON_ARGS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FORMAT_FIELD_NUMBER: _ClassVar[int]
    DATETIME_PARTITION_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    ACCESS_MODE_FIELD_NUMBER: _ClassVar[int]
    catalog: str
    schema: str
    table: str
    common_args: BatchDataSourceCommonArgs
    timestamp_format: str
    datetime_partition_columns: _containers.RepeatedCompositeFieldContainer[DatetimePartitionColumnArgs]
    access_mode: UnityCatalogAccessMode
    def __init__(self, catalog: _Optional[str] = ..., schema: _Optional[str] = ..., table: _Optional[str] = ..., common_args: _Optional[_Union[BatchDataSourceCommonArgs, _Mapping]] = ..., timestamp_format: _Optional[str] = ..., datetime_partition_columns: _Optional[_Iterable[_Union[DatetimePartitionColumnArgs, _Mapping]]] = ..., access_mode: _Optional[_Union[UnityCatalogAccessMode, str]] = ...) -> None: ...

class FileDataSourceArgs(_message.Message):
    __slots__ = ["uri", "file_format", "convert_to_glue_format", "schema_uri", "timestamp_format", "schema_override", "common_args", "datetime_partition_columns"]
    URI_FIELD_NUMBER: _ClassVar[int]
    FILE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    CONVERT_TO_GLUE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_URI_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FORMAT_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_OVERRIDE_FIELD_NUMBER: _ClassVar[int]
    COMMON_ARGS_FIELD_NUMBER: _ClassVar[int]
    DATETIME_PARTITION_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    uri: str
    file_format: str
    convert_to_glue_format: bool
    schema_uri: str
    timestamp_format: str
    schema_override: _spark_schema__client_pb2.SparkSchema
    common_args: BatchDataSourceCommonArgs
    datetime_partition_columns: _containers.RepeatedCompositeFieldContainer[DatetimePartitionColumnArgs]
    def __init__(self, uri: _Optional[str] = ..., file_format: _Optional[str] = ..., convert_to_glue_format: bool = ..., schema_uri: _Optional[str] = ..., timestamp_format: _Optional[str] = ..., schema_override: _Optional[_Union[_spark_schema__client_pb2.SparkSchema, _Mapping]] = ..., common_args: _Optional[_Union[BatchDataSourceCommonArgs, _Mapping]] = ..., datetime_partition_columns: _Optional[_Iterable[_Union[DatetimePartitionColumnArgs, _Mapping]]] = ...) -> None: ...

class Option(_message.Message):
    __slots__ = ["key", "value"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class KinesisDataSourceArgs(_message.Message):
    __slots__ = ["stream_name", "region", "initial_stream_position", "options", "common_args"]
    STREAM_NAME_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    INITIAL_STREAM_POSITION_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    COMMON_ARGS_FIELD_NUMBER: _ClassVar[int]
    stream_name: str
    region: str
    initial_stream_position: _data_source_config__client_pb2.InitialStreamPosition
    options: _containers.RepeatedCompositeFieldContainer[Option]
    common_args: StreamDataSourceCommonArgs
    def __init__(self, stream_name: _Optional[str] = ..., region: _Optional[str] = ..., initial_stream_position: _Optional[_Union[_data_source_config__client_pb2.InitialStreamPosition, str]] = ..., options: _Optional[_Iterable[_Union[Option, _Mapping]]] = ..., common_args: _Optional[_Union[StreamDataSourceCommonArgs, _Mapping]] = ...) -> None: ...

class KafkaDataSourceArgs(_message.Message):
    __slots__ = ["kafka_bootstrap_servers", "topics", "options", "ssl_keystore_location", "ssl_keystore_password_secret_id", "ssl_truststore_location", "ssl_truststore_password_secret_id", "security_protocol", "common_args"]
    KAFKA_BOOTSTRAP_SERVERS_FIELD_NUMBER: _ClassVar[int]
    TOPICS_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    SSL_KEYSTORE_LOCATION_FIELD_NUMBER: _ClassVar[int]
    SSL_KEYSTORE_PASSWORD_SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    SSL_TRUSTSTORE_LOCATION_FIELD_NUMBER: _ClassVar[int]
    SSL_TRUSTSTORE_PASSWORD_SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    SECURITY_PROTOCOL_FIELD_NUMBER: _ClassVar[int]
    COMMON_ARGS_FIELD_NUMBER: _ClassVar[int]
    kafka_bootstrap_servers: str
    topics: str
    options: _containers.RepeatedCompositeFieldContainer[Option]
    ssl_keystore_location: str
    ssl_keystore_password_secret_id: str
    ssl_truststore_location: str
    ssl_truststore_password_secret_id: str
    security_protocol: str
    common_args: StreamDataSourceCommonArgs
    def __init__(self, kafka_bootstrap_servers: _Optional[str] = ..., topics: _Optional[str] = ..., options: _Optional[_Iterable[_Union[Option, _Mapping]]] = ..., ssl_keystore_location: _Optional[str] = ..., ssl_keystore_password_secret_id: _Optional[str] = ..., ssl_truststore_location: _Optional[str] = ..., ssl_truststore_password_secret_id: _Optional[str] = ..., security_protocol: _Optional[str] = ..., common_args: _Optional[_Union[StreamDataSourceCommonArgs, _Mapping]] = ...) -> None: ...

class PushSourceArgs(_message.Message):
    __slots__ = ["log_offline", "post_processor", "input_schema", "post_processor_mode", "timestamp_field", "ingest_server_group", "transform_server_group"]
    LOG_OFFLINE_FIELD_NUMBER: _ClassVar[int]
    POST_PROCESSOR_FIELD_NUMBER: _ClassVar[int]
    INPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    POST_PROCESSOR_MODE_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_FIELD_NUMBER: _ClassVar[int]
    INGEST_SERVER_GROUP_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_SERVER_GROUP_FIELD_NUMBER: _ClassVar[int]
    log_offline: bool
    post_processor: _user_defined_function__client_pb2.UserDefinedFunction
    input_schema: _schema__client_pb2.Schema
    post_processor_mode: _transformation__client_pb2.TransformationMode
    timestamp_field: str
    ingest_server_group: str
    transform_server_group: str
    def __init__(self, log_offline: bool = ..., post_processor: _Optional[_Union[_user_defined_function__client_pb2.UserDefinedFunction, _Mapping]] = ..., input_schema: _Optional[_Union[_schema__client_pb2.Schema, _Mapping]] = ..., post_processor_mode: _Optional[_Union[_transformation__client_pb2.TransformationMode, str]] = ..., timestamp_field: _Optional[str] = ..., ingest_server_group: _Optional[str] = ..., transform_server_group: _Optional[str] = ...) -> None: ...

class RedshiftDataSourceArgs(_message.Message):
    __slots__ = ["endpoint", "table", "query", "common_args"]
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    COMMON_ARGS_FIELD_NUMBER: _ClassVar[int]
    endpoint: str
    table: str
    query: str
    common_args: BatchDataSourceCommonArgs
    def __init__(self, endpoint: _Optional[str] = ..., table: _Optional[str] = ..., query: _Optional[str] = ..., common_args: _Optional[_Union[BatchDataSourceCommonArgs, _Mapping]] = ...) -> None: ...

class SnowflakeDataSourceArgs(_message.Message):
    __slots__ = ["url", "role", "database", "schema", "warehouse", "table", "query", "common_args", "user", "password", "private_key", "private_key_passphrase"]
    URL_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    WAREHOUSE_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    COMMON_ARGS_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_KEY_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_KEY_PASSPHRASE_FIELD_NUMBER: _ClassVar[int]
    url: str
    role: str
    database: str
    schema: str
    warehouse: str
    table: str
    query: str
    common_args: BatchDataSourceCommonArgs
    user: _secret__client_pb2.SecretReference
    password: _secret__client_pb2.SecretReference
    private_key: _secret__client_pb2.SecretReference
    private_key_passphrase: _secret__client_pb2.SecretReference
    def __init__(self, url: _Optional[str] = ..., role: _Optional[str] = ..., database: _Optional[str] = ..., schema: _Optional[str] = ..., warehouse: _Optional[str] = ..., table: _Optional[str] = ..., query: _Optional[str] = ..., common_args: _Optional[_Union[BatchDataSourceCommonArgs, _Mapping]] = ..., user: _Optional[_Union[_secret__client_pb2.SecretReference, _Mapping]] = ..., password: _Optional[_Union[_secret__client_pb2.SecretReference, _Mapping]] = ..., private_key: _Optional[_Union[_secret__client_pb2.SecretReference, _Mapping]] = ..., private_key_passphrase: _Optional[_Union[_secret__client_pb2.SecretReference, _Mapping]] = ...) -> None: ...

class SparkBatchConfigArgs(_message.Message):
    __slots__ = ["data_source_function", "data_delay", "supports_time_filtering"]
    DATA_SOURCE_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    DATA_DELAY_FIELD_NUMBER: _ClassVar[int]
    SUPPORTS_TIME_FILTERING_FIELD_NUMBER: _ClassVar[int]
    data_source_function: _user_defined_function__client_pb2.UserDefinedFunction
    data_delay: _duration_pb2.Duration
    supports_time_filtering: bool
    def __init__(self, data_source_function: _Optional[_Union[_user_defined_function__client_pb2.UserDefinedFunction, _Mapping]] = ..., data_delay: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., supports_time_filtering: bool = ...) -> None: ...

class SparkStreamConfigArgs(_message.Message):
    __slots__ = ["data_source_function"]
    DATA_SOURCE_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    data_source_function: _user_defined_function__client_pb2.UserDefinedFunction
    def __init__(self, data_source_function: _Optional[_Union[_user_defined_function__client_pb2.UserDefinedFunction, _Mapping]] = ...) -> None: ...

class PandasBatchConfigArgs(_message.Message):
    __slots__ = ["data_source_function", "data_delay", "supports_time_filtering", "secrets"]
    class SecretsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _secret__client_pb2.SecretReference
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_secret__client_pb2.SecretReference, _Mapping]] = ...) -> None: ...
    DATA_SOURCE_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    DATA_DELAY_FIELD_NUMBER: _ClassVar[int]
    SUPPORTS_TIME_FILTERING_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    data_source_function: _user_defined_function__client_pb2.UserDefinedFunction
    data_delay: _duration_pb2.Duration
    supports_time_filtering: bool
    secrets: _containers.MessageMap[str, _secret__client_pb2.SecretReference]
    def __init__(self, data_source_function: _Optional[_Union[_user_defined_function__client_pb2.UserDefinedFunction, _Mapping]] = ..., data_delay: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., supports_time_filtering: bool = ..., secrets: _Optional[_Mapping[str, _secret__client_pb2.SecretReference]] = ...) -> None: ...

class PyArrowBatchConfigArgs(_message.Message):
    __slots__ = ["data_source_function", "data_delay", "supports_time_filtering", "secrets"]
    class SecretsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _secret__client_pb2.SecretReference
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_secret__client_pb2.SecretReference, _Mapping]] = ...) -> None: ...
    DATA_SOURCE_FUNCTION_FIELD_NUMBER: _ClassVar[int]
    DATA_DELAY_FIELD_NUMBER: _ClassVar[int]
    SUPPORTS_TIME_FILTERING_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    data_source_function: _user_defined_function__client_pb2.UserDefinedFunction
    data_delay: _duration_pb2.Duration
    supports_time_filtering: bool
    secrets: _containers.MessageMap[str, _secret__client_pb2.SecretReference]
    def __init__(self, data_source_function: _Optional[_Union[_user_defined_function__client_pb2.UserDefinedFunction, _Mapping]] = ..., data_delay: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., supports_time_filtering: bool = ..., secrets: _Optional[_Mapping[str, _secret__client_pb2.SecretReference]] = ...) -> None: ...

class BigqueryDataSourceArgs(_message.Message):
    __slots__ = ["project_id", "dataset", "location", "table", "query", "common_args", "credentials"]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    DATASET_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    COMMON_ARGS_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    project_id: str
    dataset: str
    location: str
    table: str
    query: str
    common_args: BatchDataSourceCommonArgs
    credentials: _secret__client_pb2.SecretReference
    def __init__(self, project_id: _Optional[str] = ..., dataset: _Optional[str] = ..., location: _Optional[str] = ..., table: _Optional[str] = ..., query: _Optional[str] = ..., common_args: _Optional[_Union[BatchDataSourceCommonArgs, _Mapping]] = ..., credentials: _Optional[_Union[_secret__client_pb2.SecretReference, _Mapping]] = ...) -> None: ...
