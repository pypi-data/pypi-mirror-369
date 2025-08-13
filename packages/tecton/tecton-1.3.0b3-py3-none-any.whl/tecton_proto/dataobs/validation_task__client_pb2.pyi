from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import fco_locator__client_pb2 as _fco_locator__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.dataobs import expectation__client_pb2 as _expectation__client_pb2
from tecton_proto.dataobs import validation__client_pb2 as _validation__client_pb2
from tecton_proto.dataobs import validation_task_params__client_pb2 as _validation_task_params__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ValidationTaskType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    VALIDATION_TASK_TYPE_UNKNOWN: _ClassVar[ValidationTaskType]
    VALIDATION_TASK_TYPE_BATCH_METRICS: _ClassVar[ValidationTaskType]
VALIDATION_TASK_TYPE_UNKNOWN: ValidationTaskType
VALIDATION_TASK_TYPE_BATCH_METRICS: ValidationTaskType

class ValidationTask(_message.Message):
    __slots__ = ["validation_job_id", "feature_view_locator", "metric_expectations", "feature_start_time", "feature_end_time", "task_type", "timeout", "dynamo_data_source", "s3_data_source"]
    VALIDATION_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_LOCATOR_FIELD_NUMBER: _ClassVar[int]
    METRIC_EXPECTATIONS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_START_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_END_TIME_FIELD_NUMBER: _ClassVar[int]
    TASK_TYPE_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_FIELD_NUMBER: _ClassVar[int]
    DYNAMO_DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    S3_DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    validation_job_id: _id__client_pb2.Id
    feature_view_locator: _fco_locator__client_pb2.IdFcoLocator
    metric_expectations: _containers.RepeatedCompositeFieldContainer[_expectation__client_pb2.MetricExpectation]
    feature_start_time: _timestamp_pb2.Timestamp
    feature_end_time: _timestamp_pb2.Timestamp
    task_type: ValidationTaskType
    timeout: _duration_pb2.Duration
    dynamo_data_source: _validation_task_params__client_pb2.DynamoDataSource
    s3_data_source: _validation_task_params__client_pb2.S3DataSource
    def __init__(self, validation_job_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., feature_view_locator: _Optional[_Union[_fco_locator__client_pb2.IdFcoLocator, _Mapping]] = ..., metric_expectations: _Optional[_Iterable[_Union[_expectation__client_pb2.MetricExpectation, _Mapping]]] = ..., feature_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., task_type: _Optional[_Union[ValidationTaskType, str]] = ..., timeout: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., dynamo_data_source: _Optional[_Union[_validation_task_params__client_pb2.DynamoDataSource, _Mapping]] = ..., s3_data_source: _Optional[_Union[_validation_task_params__client_pb2.S3DataSource, _Mapping]] = ...) -> None: ...

class ValidationTaskResult(_message.Message):
    __slots__ = ["workspace", "feature_package_id", "validation_job_id", "feature_start_time", "feature_end_time", "results", "metrics", "validation_time"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_START_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_END_TIME_FIELD_NUMBER: _ClassVar[int]
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_TIME_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    feature_package_id: _id__client_pb2.Id
    validation_job_id: _id__client_pb2.Id
    feature_start_time: _timestamp_pb2.Timestamp
    feature_end_time: _timestamp_pb2.Timestamp
    results: _containers.RepeatedCompositeFieldContainer[_validation__client_pb2.ExpectationResult]
    metrics: ValidationTaskMetrics
    validation_time: _timestamp_pb2.Timestamp
    def __init__(self, workspace: _Optional[str] = ..., feature_package_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., validation_job_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., feature_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., results: _Optional[_Iterable[_Union[_validation__client_pb2.ExpectationResult, _Mapping]]] = ..., metrics: _Optional[_Union[ValidationTaskMetrics, _Mapping]] = ..., validation_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class ValidationTaskMetrics(_message.Message):
    __slots__ = ["metric_rows_read", "feature_rows_read", "query_execution_times"]
    METRIC_ROWS_READ_FIELD_NUMBER: _ClassVar[int]
    FEATURE_ROWS_READ_FIELD_NUMBER: _ClassVar[int]
    QUERY_EXECUTION_TIMES_FIELD_NUMBER: _ClassVar[int]
    metric_rows_read: int
    feature_rows_read: int
    query_execution_times: _containers.RepeatedCompositeFieldContainer[_duration_pb2.Duration]
    def __init__(self, metric_rows_read: _Optional[int] = ..., feature_rows_read: _Optional[int] = ..., query_execution_times: _Optional[_Iterable[_Union[_duration_pb2.Duration, _Mapping]]] = ...) -> None: ...
