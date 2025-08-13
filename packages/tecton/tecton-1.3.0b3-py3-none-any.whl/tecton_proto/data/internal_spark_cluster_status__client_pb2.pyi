from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InternalSparkClusterStatusEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    INTERNAL_SPARK_CLUSTER_STATUS_UNSPECIFIED: _ClassVar[InternalSparkClusterStatusEnum]
    INTERNAL_SPARK_CLUSTER_STATUS_NO_CLUSTER: _ClassVar[InternalSparkClusterStatusEnum]
    INTERNAL_SPARK_CLUSTER_STATUS_CREATING_CLUSTER: _ClassVar[InternalSparkClusterStatusEnum]
    INTERNAL_SPARK_CLUSTER_STATUS_WAITING_FOR_CLUSTER_TO_START: _ClassVar[InternalSparkClusterStatusEnum]
    INTERNAL_SPARK_CLUSTER_STATUS_HEALTHY: _ClassVar[InternalSparkClusterStatusEnum]
    INTERNAL_SPARK_CLUSTER_STATUS_UNHEALTHY: _ClassVar[InternalSparkClusterStatusEnum]
    INTERNAL_SPARK_CLUSTER_STATUS_NOT_APPLICABLE: _ClassVar[InternalSparkClusterStatusEnum]
INTERNAL_SPARK_CLUSTER_STATUS_UNSPECIFIED: InternalSparkClusterStatusEnum
INTERNAL_SPARK_CLUSTER_STATUS_NO_CLUSTER: InternalSparkClusterStatusEnum
INTERNAL_SPARK_CLUSTER_STATUS_CREATING_CLUSTER: InternalSparkClusterStatusEnum
INTERNAL_SPARK_CLUSTER_STATUS_WAITING_FOR_CLUSTER_TO_START: InternalSparkClusterStatusEnum
INTERNAL_SPARK_CLUSTER_STATUS_HEALTHY: InternalSparkClusterStatusEnum
INTERNAL_SPARK_CLUSTER_STATUS_UNHEALTHY: InternalSparkClusterStatusEnum
INTERNAL_SPARK_CLUSTER_STATUS_NOT_APPLICABLE: InternalSparkClusterStatusEnum

class InternalSparkClusterStatus(_message.Message):
    __slots__ = ["status", "error", "error_message", "cluster_url"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_URL_FIELD_NUMBER: _ClassVar[int]
    status: InternalSparkClusterStatusEnum
    error: bool
    error_message: str
    cluster_url: str
    def __init__(self, status: _Optional[_Union[InternalSparkClusterStatusEnum, str]] = ..., error: bool = ..., error_message: _Optional[str] = ..., cluster_url: _Optional[str] = ...) -> None: ...
