from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CheckId(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    CHECK_ID_UNSPECIFIED: _ClassVar[CheckId]
    CHECK_ID_TEST_VALUE: _ClassVar[CheckId]
    CHECK_ID_TESTONLY_DATABASE_CONNECTIVITY: _ClassVar[CheckId]
    CHECK_ID_TESTONLY_CONFIGURATION_VALIDATION: _ClassVar[CheckId]
    CHECK_ID_CAN_ASSUME_CROSS_ACCOUNT_ROLES: _ClassVar[CheckId]

class ResultStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    RESULT_STATUS_UNSPECIFIED: _ClassVar[ResultStatus]
    RESULT_STATUS_PASSED: _ClassVar[ResultStatus]
    RESULT_STATUS_FAILED: _ClassVar[ResultStatus]
CHECK_ID_UNSPECIFIED: CheckId
CHECK_ID_TEST_VALUE: CheckId
CHECK_ID_TESTONLY_DATABASE_CONNECTIVITY: CheckId
CHECK_ID_TESTONLY_CONFIGURATION_VALIDATION: CheckId
CHECK_ID_CAN_ASSUME_CROSS_ACCOUNT_ROLES: CheckId
RESULT_STATUS_UNSPECIFIED: ResultStatus
RESULT_STATUS_PASSED: ResultStatus
RESULT_STATUS_FAILED: ResultStatus
SHORT_NAME_FIELD_NUMBER: _ClassVar[int]
short_name: _descriptor.FieldDescriptor
DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
description: _descriptor.FieldDescriptor

class CheckResult(_message.Message):
    __slots__ = ["short_name", "description", "start_time", "status", "error_message", "last_passed_time"]
    SHORT_NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    LAST_PASSED_TIME_FIELD_NUMBER: _ClassVar[int]
    short_name: str
    description: str
    start_time: _timestamp_pb2.Timestamp
    status: ResultStatus
    error_message: str
    last_passed_time: _timestamp_pb2.Timestamp
    def __init__(self, short_name: _Optional[str] = ..., description: _Optional[str] = ..., start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[_Union[ResultStatus, str]] = ..., error_message: _Optional[str] = ..., last_passed_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class CheckRun(_message.Message):
    __slots__ = ["completed_time", "check_results"]
    COMPLETED_TIME_FIELD_NUMBER: _ClassVar[int]
    CHECK_RESULTS_FIELD_NUMBER: _ClassVar[int]
    completed_time: _timestamp_pb2.Timestamp
    check_results: _containers.RepeatedCompositeFieldContainer[CheckResult]
    def __init__(self, completed_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., check_results: _Optional[_Iterable[_Union[CheckResult, _Mapping]]] = ...) -> None: ...
