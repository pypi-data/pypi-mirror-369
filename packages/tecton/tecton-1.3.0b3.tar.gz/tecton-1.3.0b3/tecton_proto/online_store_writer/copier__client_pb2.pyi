from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.data import feature_view__client_pb2 as _feature_view__client_pb2
from tecton_proto.online_store_writer import config__client_pb2 as _config__client_pb2
from tecton_proto.snowflake import snowflake_credentials__client_pb2 as _snowflake_credentials__client_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TimestampUnit(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNSPECIFIED: _ClassVar[TimestampUnit]
    MILLIS: _ClassVar[TimestampUnit]
    MICROS: _ClassVar[TimestampUnit]
UNSPECIFIED: TimestampUnit
MILLIS: TimestampUnit
MICROS: TimestampUnit

class OnlineStoreCopierRequest(_message.Message):
    __slots__ = ["online_store_writer_configuration", "feature_view", "materialization_task_attempt_id", "task_key", "attempt_index", "sqs_url", "online_store_metadata_configuration", "enable_new_consumption_metrics", "object_copy_request", "status_update_request", "deletion_request"]
    ONLINE_STORE_WRITER_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_TASK_ATTEMPT_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_KEY_FIELD_NUMBER: _ClassVar[int]
    ATTEMPT_INDEX_FIELD_NUMBER: _ClassVar[int]
    SQS_URL_FIELD_NUMBER: _ClassVar[int]
    ONLINE_STORE_METADATA_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    ENABLE_NEW_CONSUMPTION_METRICS_FIELD_NUMBER: _ClassVar[int]
    OBJECT_COPY_REQUEST_FIELD_NUMBER: _ClassVar[int]
    STATUS_UPDATE_REQUEST_FIELD_NUMBER: _ClassVar[int]
    DELETION_REQUEST_FIELD_NUMBER: _ClassVar[int]
    online_store_writer_configuration: _config__client_pb2.OnlineStoreWriterConfiguration
    feature_view: _feature_view__client_pb2.FeatureView
    materialization_task_attempt_id: _id__client_pb2.Id
    task_key: str
    attempt_index: int
    sqs_url: str
    online_store_metadata_configuration: _config__client_pb2.OnlineStoreMetadataConfiguration
    enable_new_consumption_metrics: bool
    object_copy_request: ObjectCopyRequest
    status_update_request: StatusUpdateRequest
    deletion_request: DeletionRequest
    def __init__(self, online_store_writer_configuration: _Optional[_Union[_config__client_pb2.OnlineStoreWriterConfiguration, _Mapping]] = ..., feature_view: _Optional[_Union[_feature_view__client_pb2.FeatureView, _Mapping]] = ..., materialization_task_attempt_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., task_key: _Optional[str] = ..., attempt_index: _Optional[int] = ..., sqs_url: _Optional[str] = ..., online_store_metadata_configuration: _Optional[_Union[_config__client_pb2.OnlineStoreMetadataConfiguration, _Mapping]] = ..., enable_new_consumption_metrics: bool = ..., object_copy_request: _Optional[_Union[ObjectCopyRequest, _Mapping]] = ..., status_update_request: _Optional[_Union[StatusUpdateRequest, _Mapping]] = ..., deletion_request: _Optional[_Union[DeletionRequest, _Mapping]] = ...) -> None: ...

class S3Stage(_message.Message):
    __slots__ = ["bucket", "key"]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    bucket: str
    key: str
    def __init__(self, bucket: _Optional[str] = ..., key: _Optional[str] = ...) -> None: ...

class GCSStage(_message.Message):
    __slots__ = ["bucket", "blob"]
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    BLOB_FIELD_NUMBER: _ClassVar[int]
    bucket: str
    blob: str
    def __init__(self, bucket: _Optional[str] = ..., blob: _Optional[str] = ...) -> None: ...

class SnowflakeInternalStage(_message.Message):
    __slots__ = ["snowflake_account_identifier", "credentials", "location"]
    SNOWFLAKE_ACCOUNT_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    snowflake_account_identifier: str
    credentials: _snowflake_credentials__client_pb2.SnowflakeCredentials
    location: str
    def __init__(self, snowflake_account_identifier: _Optional[str] = ..., credentials: _Optional[_Union[_snowflake_credentials__client_pb2.SnowflakeCredentials, _Mapping]] = ..., location: _Optional[str] = ...) -> None: ...

class LocalFileStage(_message.Message):
    __slots__ = ["location"]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    location: str
    def __init__(self, location: _Optional[str] = ...) -> None: ...

class ObjectCopyRequest(_message.Message):
    __slots__ = ["s3_stage", "snowflake_internal_stage", "local_file_stage", "gcs_stage", "skip_rows", "timestamp_units"]
    S3_STAGE_FIELD_NUMBER: _ClassVar[int]
    SNOWFLAKE_INTERNAL_STAGE_FIELD_NUMBER: _ClassVar[int]
    LOCAL_FILE_STAGE_FIELD_NUMBER: _ClassVar[int]
    GCS_STAGE_FIELD_NUMBER: _ClassVar[int]
    SKIP_ROWS_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_UNITS_FIELD_NUMBER: _ClassVar[int]
    s3_stage: S3Stage
    snowflake_internal_stage: SnowflakeInternalStage
    local_file_stage: LocalFileStage
    gcs_stage: GCSStage
    skip_rows: int
    timestamp_units: TimestampUnit
    def __init__(self, s3_stage: _Optional[_Union[S3Stage, _Mapping]] = ..., snowflake_internal_stage: _Optional[_Union[SnowflakeInternalStage, _Mapping]] = ..., local_file_stage: _Optional[_Union[LocalFileStage, _Mapping]] = ..., gcs_stage: _Optional[_Union[GCSStage, _Mapping]] = ..., skip_rows: _Optional[int] = ..., timestamp_units: _Optional[_Union[TimestampUnit, str]] = ...) -> None: ...

class StatusUpdateRequest(_message.Message):
    __slots__ = ["anchor_time", "materialized_raw_data_end_time"]
    ANCHOR_TIME_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZED_RAW_DATA_END_TIME_FIELD_NUMBER: _ClassVar[int]
    anchor_time: _timestamp_pb2.Timestamp
    materialized_raw_data_end_time: _timestamp_pb2.Timestamp
    def __init__(self, anchor_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., materialized_raw_data_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DeletionRequest(_message.Message):
    __slots__ = ["online_join_keys_path", "online_join_keys_full_path"]
    ONLINE_JOIN_KEYS_PATH_FIELD_NUMBER: _ClassVar[int]
    ONLINE_JOIN_KEYS_FULL_PATH_FIELD_NUMBER: _ClassVar[int]
    online_join_keys_path: str
    online_join_keys_full_path: str
    def __init__(self, online_join_keys_path: _Optional[str] = ..., online_join_keys_full_path: _Optional[str] = ...) -> None: ...
