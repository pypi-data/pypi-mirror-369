from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import aws_credentials__client_pb2 as _aws_credentials__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.data import feature_view__client_pb2 as _feature_view__client_pb2
from tecton_proto.data import user_deployment_settings__client_pb2 as _user_deployment_settings__client_pb2
from tecton_proto.dataobs import expectation__client_pb2 as _expectation__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ValidationTaskParams(_message.Message):
    __slots__ = ["validation_job_id", "task_id", "workspace_name", "feature_view", "metric_expectations", "dynamo_data_source", "s3_data_source", "result_location", "result_key"]
    VALIDATION_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    METRIC_EXPECTATIONS_FIELD_NUMBER: _ClassVar[int]
    DYNAMO_DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    S3_DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    RESULT_LOCATION_FIELD_NUMBER: _ClassVar[int]
    RESULT_KEY_FIELD_NUMBER: _ClassVar[int]
    validation_job_id: _id__client_pb2.Id
    task_id: int
    workspace_name: str
    feature_view: _feature_view__client_pb2.FeatureView
    metric_expectations: _containers.RepeatedCompositeFieldContainer[_expectation__client_pb2.MetricExpectation]
    dynamo_data_source: DynamoDataSource
    s3_data_source: S3DataSource
    result_location: _user_deployment_settings__client_pb2.S3Location
    result_key: str
    def __init__(self, validation_job_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., task_id: _Optional[int] = ..., workspace_name: _Optional[str] = ..., feature_view: _Optional[_Union[_feature_view__client_pb2.FeatureView, _Mapping]] = ..., metric_expectations: _Optional[_Iterable[_Union[_expectation__client_pb2.MetricExpectation, _Mapping]]] = ..., dynamo_data_source: _Optional[_Union[DynamoDataSource, _Mapping]] = ..., s3_data_source: _Optional[_Union[S3DataSource, _Mapping]] = ..., result_location: _Optional[_Union[_user_deployment_settings__client_pb2.S3Location, _Mapping]] = ..., result_key: _Optional[str] = ...) -> None: ...

class DynamoDataSource(_message.Message):
    __slots__ = ["dynamo_role", "table_name", "metric_interval", "feature_start_time", "feature_end_time"]
    DYNAMO_ROLE_FIELD_NUMBER: _ClassVar[int]
    TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    METRIC_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    FEATURE_START_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_END_TIME_FIELD_NUMBER: _ClassVar[int]
    dynamo_role: _aws_credentials__client_pb2.AwsIamRole
    table_name: str
    metric_interval: _duration_pb2.Duration
    feature_start_time: _timestamp_pb2.Timestamp
    feature_end_time: _timestamp_pb2.Timestamp
    def __init__(self, dynamo_role: _Optional[_Union[_aws_credentials__client_pb2.AwsIamRole, _Mapping]] = ..., table_name: _Optional[str] = ..., metric_interval: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., feature_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class S3DataSource(_message.Message):
    __slots__ = ["location"]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    location: str
    def __init__(self, location: _Optional[str] = ...) -> None: ...
