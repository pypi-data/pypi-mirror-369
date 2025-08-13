from google.protobuf import duration_pb2 as _duration_pb2
from tecton_proto.dataobs import expectation__client_pb2 as _expectation__client_pb2
from tecton_proto.dataobs import metric__client_pb2 as _metric__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataObservabilityConfig(_message.Message):
    __slots__ = ["workspace", "feature_view_name", "feature_expectation_validation_schedule", "metrics", "feature_expectations", "metric_expectations"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_EXPECTATION_VALIDATION_SCHEDULE_FIELD_NUMBER: _ClassVar[int]
    METRICS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_EXPECTATIONS_FIELD_NUMBER: _ClassVar[int]
    METRIC_EXPECTATIONS_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    feature_view_name: str
    feature_expectation_validation_schedule: str
    metrics: _containers.RepeatedCompositeFieldContainer[_metric__client_pb2.Metric]
    feature_expectations: _containers.RepeatedCompositeFieldContainer[_expectation__client_pb2.FeatureExpectation]
    metric_expectations: _containers.RepeatedCompositeFieldContainer[_expectation__client_pb2.MetricExpectation]
    def __init__(self, workspace: _Optional[str] = ..., feature_view_name: _Optional[str] = ..., feature_expectation_validation_schedule: _Optional[str] = ..., metrics: _Optional[_Iterable[_Union[_metric__client_pb2.Metric, _Mapping]]] = ..., feature_expectations: _Optional[_Iterable[_Union[_expectation__client_pb2.FeatureExpectation, _Mapping]]] = ..., metric_expectations: _Optional[_Iterable[_Union[_expectation__client_pb2.MetricExpectation, _Mapping]]] = ...) -> None: ...

class DataObservabilityMaterializationConfig(_message.Message):
    __slots__ = ["enabled", "metric_interval", "metric_table_name"]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    METRIC_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    METRIC_TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    metric_interval: _duration_pb2.Duration
    metric_table_name: str
    def __init__(self, enabled: bool = ..., metric_interval: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., metric_table_name: _Optional[str] = ...) -> None: ...
