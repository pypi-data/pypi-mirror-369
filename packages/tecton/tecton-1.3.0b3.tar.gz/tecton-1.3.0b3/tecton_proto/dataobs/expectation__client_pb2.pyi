from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.dataobs import metric__client_pb2 as _metric__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FeatureExpectation(_message.Message):
    __slots__ = ["name", "expression", "alert_message_template", "input_column_names", "creation_time", "last_update_time"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    ALERT_MESSAGE_TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    INPUT_COLUMN_NAMES_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    name: str
    expression: str
    alert_message_template: str
    input_column_names: _containers.RepeatedScalarFieldContainer[str]
    creation_time: _timestamp_pb2.Timestamp
    last_update_time: _timestamp_pb2.Timestamp
    def __init__(self, name: _Optional[str] = ..., expression: _Optional[str] = ..., alert_message_template: _Optional[str] = ..., input_column_names: _Optional[_Iterable[str]] = ..., creation_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_update_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class MetricExpectation(_message.Message):
    __slots__ = ["name", "display_name", "expression", "alert_message_template", "input_metrics", "creation_time", "last_update_time"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    EXPRESSION_FIELD_NUMBER: _ClassVar[int]
    ALERT_MESSAGE_TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    INPUT_METRICS_FIELD_NUMBER: _ClassVar[int]
    CREATION_TIME_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATE_TIME_FIELD_NUMBER: _ClassVar[int]
    name: str
    display_name: str
    expression: str
    alert_message_template: str
    input_metrics: _containers.RepeatedCompositeFieldContainer[_metric__client_pb2.FeatureMetric]
    creation_time: _timestamp_pb2.Timestamp
    last_update_time: _timestamp_pb2.Timestamp
    def __init__(self, name: _Optional[str] = ..., display_name: _Optional[str] = ..., expression: _Optional[str] = ..., alert_message_template: _Optional[str] = ..., input_metrics: _Optional[_Iterable[_Union[_metric__client_pb2.FeatureMetric, _Mapping]]] = ..., creation_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., last_update_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
