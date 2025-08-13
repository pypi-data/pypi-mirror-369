from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.dataobs import expectation__client_pb2 as _expectation__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ExpectationResultEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    RESULT_UNKNOWN: _ClassVar[ExpectationResultEnum]
    RESULT_PASSED: _ClassVar[ExpectationResultEnum]
    RESULT_FAILED: _ClassVar[ExpectationResultEnum]
    RESULT_ERROR: _ClassVar[ExpectationResultEnum]
RESULT_UNKNOWN: ExpectationResultEnum
RESULT_PASSED: ExpectationResultEnum
RESULT_FAILED: ExpectationResultEnum
RESULT_ERROR: ExpectationResultEnum

class ExpectationResult(_message.Message):
    __slots__ = ["validation_job_id", "workspace", "feature_view_name", "feature_package_id", "validation_time", "feature_interval_start_time", "feature_interval_end_time", "feature_expectation_metadata", "metric_expectation_metadata", "result", "result_id"]
    VALIDATION_JOB_ID_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_INTERVAL_START_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_INTERVAL_END_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_EXPECTATION_METADATA_FIELD_NUMBER: _ClassVar[int]
    METRIC_EXPECTATION_METADATA_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    RESULT_ID_FIELD_NUMBER: _ClassVar[int]
    validation_job_id: _id__client_pb2.Id
    workspace: str
    feature_view_name: str
    feature_package_id: _id__client_pb2.Id
    validation_time: _timestamp_pb2.Timestamp
    feature_interval_start_time: _timestamp_pb2.Timestamp
    feature_interval_end_time: _timestamp_pb2.Timestamp
    feature_expectation_metadata: FeatureExpectationMetadata
    metric_expectation_metadata: MetricExpectationMetadata
    result: ExpectationResultEnum
    result_id: _id__client_pb2.Id
    def __init__(self, validation_job_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., workspace: _Optional[str] = ..., feature_view_name: _Optional[str] = ..., feature_package_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., validation_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_interval_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_interval_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_expectation_metadata: _Optional[_Union[FeatureExpectationMetadata, _Mapping]] = ..., metric_expectation_metadata: _Optional[_Union[MetricExpectationMetadata, _Mapping]] = ..., result: _Optional[_Union[ExpectationResultEnum, str]] = ..., result_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ...) -> None: ...

class FeatureExpectationMetadata(_message.Message):
    __slots__ = ["expectation", "alert_msg", "failure_percentage", "failed_join_key_samples"]
    EXPECTATION_FIELD_NUMBER: _ClassVar[int]
    ALERT_MSG_FIELD_NUMBER: _ClassVar[int]
    FAILURE_PERCENTAGE_FIELD_NUMBER: _ClassVar[int]
    FAILED_JOIN_KEY_SAMPLES_FIELD_NUMBER: _ClassVar[int]
    expectation: _expectation__client_pb2.FeatureExpectation
    alert_msg: str
    failure_percentage: float
    failed_join_key_samples: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, expectation: _Optional[_Union[_expectation__client_pb2.FeatureExpectation, _Mapping]] = ..., alert_msg: _Optional[str] = ..., failure_percentage: _Optional[float] = ..., failed_join_key_samples: _Optional[_Iterable[str]] = ...) -> None: ...

class MetricExpectationMetadata(_message.Message):
    __slots__ = ["expectation", "alert_msg", "param_values"]
    class ParamValue(_message.Message):
        __slots__ = ["metric_name", "actual_value", "interval_start_time"]
        METRIC_NAME_FIELD_NUMBER: _ClassVar[int]
        ACTUAL_VALUE_FIELD_NUMBER: _ClassVar[int]
        INTERVAL_START_TIME_FIELD_NUMBER: _ClassVar[int]
        metric_name: str
        actual_value: str
        interval_start_time: _timestamp_pb2.Timestamp
        def __init__(self, metric_name: _Optional[str] = ..., actual_value: _Optional[str] = ..., interval_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
    EXPECTATION_FIELD_NUMBER: _ClassVar[int]
    ALERT_MSG_FIELD_NUMBER: _ClassVar[int]
    PARAM_VALUES_FIELD_NUMBER: _ClassVar[int]
    expectation: _expectation__client_pb2.MetricExpectation
    alert_msg: str
    param_values: _containers.RepeatedCompositeFieldContainer[MetricExpectationMetadata.ParamValue]
    def __init__(self, expectation: _Optional[_Union[_expectation__client_pb2.MetricExpectation, _Mapping]] = ..., alert_msg: _Optional[str] = ..., param_values: _Optional[_Iterable[_Union[MetricExpectationMetadata.ParamValue, _Mapping]]] = ...) -> None: ...

class ResultSummary(_message.Message):
    __slots__ = ["passed", "failed", "error", "unknown"]
    PASSED_FIELD_NUMBER: _ClassVar[int]
    FAILED_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    UNKNOWN_FIELD_NUMBER: _ClassVar[int]
    passed: int
    failed: int
    error: int
    unknown: int
    def __init__(self, passed: _Optional[int] = ..., failed: _Optional[int] = ..., error: _Optional[int] = ..., unknown: _Optional[int] = ...) -> None: ...

class WorkspaceResultSummary(_message.Message):
    __slots__ = ["workspace", "summary", "feature_view_summary"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_SUMMARY_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    summary: ResultSummary
    feature_view_summary: _containers.RepeatedCompositeFieldContainer[FeatureViewResultSummary]
    def __init__(self, workspace: _Optional[str] = ..., summary: _Optional[_Union[ResultSummary, _Mapping]] = ..., feature_view_summary: _Optional[_Iterable[_Union[FeatureViewResultSummary, _Mapping]]] = ...) -> None: ...

class FeatureViewResultSummary(_message.Message):
    __slots__ = ["feature_view_name", "summary", "expectation_summary"]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    EXPECTATION_SUMMARY_FIELD_NUMBER: _ClassVar[int]
    feature_view_name: str
    summary: ResultSummary
    expectation_summary: _containers.RepeatedCompositeFieldContainer[ExpectationResultSummary]
    def __init__(self, feature_view_name: _Optional[str] = ..., summary: _Optional[_Union[ResultSummary, _Mapping]] = ..., expectation_summary: _Optional[_Iterable[_Union[ExpectationResultSummary, _Mapping]]] = ...) -> None: ...

class ExpectationResultSummary(_message.Message):
    __slots__ = ["expectation_name", "summary"]
    EXPECTATION_NAME_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    expectation_name: str
    summary: ResultSummary
    def __init__(self, expectation_name: _Optional[str] = ..., summary: _Optional[_Union[ResultSummary, _Mapping]] = ...) -> None: ...
