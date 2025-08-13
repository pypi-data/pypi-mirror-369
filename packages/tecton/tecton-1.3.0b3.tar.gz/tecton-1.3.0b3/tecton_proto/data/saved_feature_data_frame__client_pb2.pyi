from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import schema__client_pb2 as _schema__client_pb2
from tecton_proto.common import spark_schema__client_pb2 as _spark_schema__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SavedFeatureDataFrameType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    NOT_SET: _ClassVar[SavedFeatureDataFrameType]
    SAVED: _ClassVar[SavedFeatureDataFrameType]
    LOGGED: _ClassVar[SavedFeatureDataFrameType]

class SavedFeatureDataFrameFormat(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    SAVED_FEATURED_DATAFRAME_FORMAT_UNSPECIFIED: _ClassVar[SavedFeatureDataFrameFormat]
    SAVED_FEATURED_DATAFRAME_FORMAT_LEGACY: _ClassVar[SavedFeatureDataFrameFormat]
    SAVED_FEATURED_DATAFRAME_FORMAT_UNIFIED_STORAGE: _ClassVar[SavedFeatureDataFrameFormat]
NOT_SET: SavedFeatureDataFrameType
SAVED: SavedFeatureDataFrameType
LOGGED: SavedFeatureDataFrameType
SAVED_FEATURED_DATAFRAME_FORMAT_UNSPECIFIED: SavedFeatureDataFrameFormat
SAVED_FEATURED_DATAFRAME_FORMAT_LEGACY: SavedFeatureDataFrameFormat
SAVED_FEATURED_DATAFRAME_FORMAT_UNIFIED_STORAGE: SavedFeatureDataFrameFormat

class SavedFeatureDataFrameInfo(_message.Message):
    __slots__ = ["name", "created_at", "is_archived", "workspace", "is_data_deleted", "data_deleted_at"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_ARCHIVED_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    IS_DATA_DELETED_FIELD_NUMBER: _ClassVar[int]
    DATA_DELETED_AT_FIELD_NUMBER: _ClassVar[int]
    name: str
    created_at: _timestamp_pb2.Timestamp
    is_archived: bool
    workspace: str
    is_data_deleted: bool
    data_deleted_at: _timestamp_pb2.Timestamp
    def __init__(self, name: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., is_archived: bool = ..., workspace: _Optional[str] = ..., is_data_deleted: bool = ..., data_deleted_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class SavedFeatureDataFrame(_message.Message):
    __slots__ = ["saved_feature_dataframe_id", "info", "dataframe_location", "feature_package_id", "feature_service_id", "feature_package_name", "feature_service_name", "state_update_entry_commit_id", "join_key_column_names", "timestamp_column_name", "schema", "type", "format", "unified_schema", "saved_dataset", "logged_dataset"]
    SAVED_FEATURE_DATAFRAME_ID_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    DATAFRAME_LOCATION_FIELD_NUMBER: _ClassVar[int]
    FEATURE_PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_PACKAGE_NAME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    STATE_UPDATE_ENTRY_COMMIT_ID_FIELD_NUMBER: _ClassVar[int]
    JOIN_KEY_COLUMN_NAMES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FORMAT_FIELD_NUMBER: _ClassVar[int]
    UNIFIED_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SAVED_DATASET_FIELD_NUMBER: _ClassVar[int]
    LOGGED_DATASET_FIELD_NUMBER: _ClassVar[int]
    saved_feature_dataframe_id: _id__client_pb2.Id
    info: SavedFeatureDataFrameInfo
    dataframe_location: str
    feature_package_id: _id__client_pb2.Id
    feature_service_id: _id__client_pb2.Id
    feature_package_name: str
    feature_service_name: str
    state_update_entry_commit_id: str
    join_key_column_names: _containers.RepeatedScalarFieldContainer[str]
    timestamp_column_name: str
    schema: _spark_schema__client_pb2.SparkSchema
    type: SavedFeatureDataFrameType
    format: SavedFeatureDataFrameFormat
    unified_schema: _schema__client_pb2.Schema
    saved_dataset: SavedDataset
    logged_dataset: LoggedDataset
    def __init__(self, saved_feature_dataframe_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., info: _Optional[_Union[SavedFeatureDataFrameInfo, _Mapping]] = ..., dataframe_location: _Optional[str] = ..., feature_package_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., feature_service_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., feature_package_name: _Optional[str] = ..., feature_service_name: _Optional[str] = ..., state_update_entry_commit_id: _Optional[str] = ..., join_key_column_names: _Optional[_Iterable[str]] = ..., timestamp_column_name: _Optional[str] = ..., schema: _Optional[_Union[_spark_schema__client_pb2.SparkSchema, _Mapping]] = ..., type: _Optional[_Union[SavedFeatureDataFrameType, str]] = ..., format: _Optional[_Union[SavedFeatureDataFrameFormat, str]] = ..., unified_schema: _Optional[_Union[_schema__client_pb2.Schema, _Mapping]] = ..., saved_dataset: _Optional[_Union[SavedDataset, _Mapping]] = ..., logged_dataset: _Optional[_Union[LoggedDataset, _Mapping]] = ...) -> None: ...

class SavedDataset(_message.Message):
    __slots__ = ["creation_task_id", "event_column_names", "timestamp_column_name"]
    CREATION_TASK_ID_FIELD_NUMBER: _ClassVar[int]
    EVENT_COLUMN_NAMES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    creation_task_id: _id__client_pb2.Id
    event_column_names: _containers.RepeatedScalarFieldContainer[str]
    timestamp_column_name: str
    def __init__(self, creation_task_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., event_column_names: _Optional[_Iterable[str]] = ..., timestamp_column_name: _Optional[str] = ...) -> None: ...

class LoggedDataset(_message.Message):
    __slots__ = ["join_key_column_names", "timestamp_column_name"]
    JOIN_KEY_COLUMN_NAMES_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    join_key_column_names: _containers.RepeatedScalarFieldContainer[str]
    timestamp_column_name: str
    def __init__(self, join_key_column_names: _Optional[_Iterable[str]] = ..., timestamp_column_name: _Optional[str] = ...) -> None: ...
