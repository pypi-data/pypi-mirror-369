from tecton_proto.spark_common import clusters__client_pb2 as _clusters__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ClusterState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    PENDING: _ClassVar[ClusterState]
    RUNNING: _ClassVar[ClusterState]
    RESTARTING: _ClassVar[ClusterState]
    RESIZING: _ClassVar[ClusterState]
    TERMINATING: _ClassVar[ClusterState]
    TERMINATED: _ClassVar[ClusterState]
    ERROR: _ClassVar[ClusterState]
    UNKNOWN: _ClassVar[ClusterState]

class TerminationCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNKNOWN_TERMINATION_STATE: _ClassVar[TerminationCode]
    USER_REQUEST: _ClassVar[TerminationCode]
    JOB_FINISHED: _ClassVar[TerminationCode]
    INACTIVITY: _ClassVar[TerminationCode]
    CLOUD_PROVIDER_SHUTDOWN: _ClassVar[TerminationCode]
    COMMUNICATION_LOST: _ClassVar[TerminationCode]
    CLOUD_PROVIDER_LAUNCH_FAILURE: _ClassVar[TerminationCode]
    SPARK_STARTUP_FAILURE: _ClassVar[TerminationCode]
    INVALID_ARGUMENT: _ClassVar[TerminationCode]
    UNEXPECTED_LAUNCH_FAILURE: _ClassVar[TerminationCode]
    INTERNAL_ERROR: _ClassVar[TerminationCode]
    SPARK_ERROR: _ClassVar[TerminationCode]
    METASTORE_COMPONENT_UNHEALTHY: _ClassVar[TerminationCode]
    DBFS_COMPONENT_UNHEALTHY: _ClassVar[TerminationCode]
    DRIVER_UNREACHABLE: _ClassVar[TerminationCode]
    DRIVER_UNRESPONSIVE: _ClassVar[TerminationCode]
    INSTANCE_UNREACHABLE: _ClassVar[TerminationCode]
    CONTAINER_LAUNCH_FAILURE: _ClassVar[TerminationCode]
    INSTANCE_POOL_CLUSTER_FAILURE: _ClassVar[TerminationCode]
    REQUEST_REJECTED: _ClassVar[TerminationCode]
    INIT_SCRIPT_FAILURE: _ClassVar[TerminationCode]
    TRIAL_EXPIRED: _ClassVar[TerminationCode]
    AWS_INSUFFICIENT_INSTANCE_CAPACITY_FAILURE: _ClassVar[TerminationCode]

class TerminationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNKNOWN_TERMINATION_TYPE: _ClassVar[TerminationType]
    SUCCESS: _ClassVar[TerminationType]
    CLIENT_ERROR: _ClassVar[TerminationType]
    SERVICE_FAULT: _ClassVar[TerminationType]
    CLOUD_FAILURE: _ClassVar[TerminationType]
PENDING: ClusterState
RUNNING: ClusterState
RESTARTING: ClusterState
RESIZING: ClusterState
TERMINATING: ClusterState
TERMINATED: ClusterState
ERROR: ClusterState
UNKNOWN: ClusterState
UNKNOWN_TERMINATION_STATE: TerminationCode
USER_REQUEST: TerminationCode
JOB_FINISHED: TerminationCode
INACTIVITY: TerminationCode
CLOUD_PROVIDER_SHUTDOWN: TerminationCode
COMMUNICATION_LOST: TerminationCode
CLOUD_PROVIDER_LAUNCH_FAILURE: TerminationCode
SPARK_STARTUP_FAILURE: TerminationCode
INVALID_ARGUMENT: TerminationCode
UNEXPECTED_LAUNCH_FAILURE: TerminationCode
INTERNAL_ERROR: TerminationCode
SPARK_ERROR: TerminationCode
METASTORE_COMPONENT_UNHEALTHY: TerminationCode
DBFS_COMPONENT_UNHEALTHY: TerminationCode
DRIVER_UNREACHABLE: TerminationCode
DRIVER_UNRESPONSIVE: TerminationCode
INSTANCE_UNREACHABLE: TerminationCode
CONTAINER_LAUNCH_FAILURE: TerminationCode
INSTANCE_POOL_CLUSTER_FAILURE: TerminationCode
REQUEST_REJECTED: TerminationCode
INIT_SCRIPT_FAILURE: TerminationCode
TRIAL_EXPIRED: TerminationCode
AWS_INSUFFICIENT_INSTANCE_CAPACITY_FAILURE: TerminationCode
UNKNOWN_TERMINATION_TYPE: TerminationType
SUCCESS: TerminationType
CLIENT_ERROR: TerminationType
SERVICE_FAULT: TerminationType
CLOUD_FAILURE: TerminationType

class ClustersGetRequest(_message.Message):
    __slots__ = ["cluster_id"]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    cluster_id: str
    def __init__(self, cluster_id: _Optional[str] = ...) -> None: ...

class ClusterCreateRequest(_message.Message):
    __slots__ = ["spark_conf", "driver_node_type_id", "node_type_id", "num_workers", "cluster_name", "spark_version", "aws_attributes", "idempotency_token", "spark_env_vars", "custom_tags", "autotermination_minutes", "enable_elastic_disk", "autoscale", "init_scripts", "policy_id", "gcp_attributes", "data_security_mode", "single_user_name", "apply_policy_default_values"]
    class SparkConfEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class SparkEnvVarsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class CustomTagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SPARK_CONF_FIELD_NUMBER: _ClassVar[int]
    DRIVER_NODE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    NUM_WORKERS_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    SPARK_VERSION_FIELD_NUMBER: _ClassVar[int]
    AWS_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    IDEMPOTENCY_TOKEN_FIELD_NUMBER: _ClassVar[int]
    SPARK_ENV_VARS_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_TAGS_FIELD_NUMBER: _ClassVar[int]
    AUTOTERMINATION_MINUTES_FIELD_NUMBER: _ClassVar[int]
    ENABLE_ELASTIC_DISK_FIELD_NUMBER: _ClassVar[int]
    AUTOSCALE_FIELD_NUMBER: _ClassVar[int]
    INIT_SCRIPTS_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    GCP_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    DATA_SECURITY_MODE_FIELD_NUMBER: _ClassVar[int]
    SINGLE_USER_NAME_FIELD_NUMBER: _ClassVar[int]
    APPLY_POLICY_DEFAULT_VALUES_FIELD_NUMBER: _ClassVar[int]
    spark_conf: _containers.ScalarMap[str, str]
    driver_node_type_id: str
    node_type_id: str
    num_workers: int
    cluster_name: str
    spark_version: str
    aws_attributes: _clusters__client_pb2.AwsAttributes
    idempotency_token: str
    spark_env_vars: _containers.ScalarMap[str, str]
    custom_tags: _containers.ScalarMap[str, str]
    autotermination_minutes: int
    enable_elastic_disk: bool
    autoscale: ClusterAutoScale
    init_scripts: _containers.RepeatedCompositeFieldContainer[_clusters__client_pb2.ResourceLocation]
    policy_id: str
    gcp_attributes: _clusters__client_pb2.GCPAttributes
    data_security_mode: str
    single_user_name: str
    apply_policy_default_values: bool
    def __init__(self, spark_conf: _Optional[_Mapping[str, str]] = ..., driver_node_type_id: _Optional[str] = ..., node_type_id: _Optional[str] = ..., num_workers: _Optional[int] = ..., cluster_name: _Optional[str] = ..., spark_version: _Optional[str] = ..., aws_attributes: _Optional[_Union[_clusters__client_pb2.AwsAttributes, _Mapping]] = ..., idempotency_token: _Optional[str] = ..., spark_env_vars: _Optional[_Mapping[str, str]] = ..., custom_tags: _Optional[_Mapping[str, str]] = ..., autotermination_minutes: _Optional[int] = ..., enable_elastic_disk: bool = ..., autoscale: _Optional[_Union[ClusterAutoScale, _Mapping]] = ..., init_scripts: _Optional[_Iterable[_Union[_clusters__client_pb2.ResourceLocation, _Mapping]]] = ..., policy_id: _Optional[str] = ..., gcp_attributes: _Optional[_Union[_clusters__client_pb2.GCPAttributes, _Mapping]] = ..., data_security_mode: _Optional[str] = ..., single_user_name: _Optional[str] = ..., apply_policy_default_values: bool = ...) -> None: ...

class ClusterAutoScale(_message.Message):
    __slots__ = ["min_workers", "max_workers"]
    MIN_WORKERS_FIELD_NUMBER: _ClassVar[int]
    MAX_WORKERS_FIELD_NUMBER: _ClassVar[int]
    min_workers: int
    max_workers: int
    def __init__(self, min_workers: _Optional[int] = ..., max_workers: _Optional[int] = ...) -> None: ...

class ClusterCreateResponse(_message.Message):
    __slots__ = ["cluster_id"]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    cluster_id: str
    def __init__(self, cluster_id: _Optional[str] = ...) -> None: ...

class ClusterTerminateRequest(_message.Message):
    __slots__ = ["cluster_id"]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    cluster_id: str
    def __init__(self, cluster_id: _Optional[str] = ...) -> None: ...

class ClustersGetResponse(_message.Message):
    __slots__ = ["cluster_id", "state_message", "termination_reason", "state"]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_REASON_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    cluster_id: str
    state_message: str
    termination_reason: TerminationReason
    state: ClusterState
    def __init__(self, cluster_id: _Optional[str] = ..., state_message: _Optional[str] = ..., termination_reason: _Optional[_Union[TerminationReason, _Mapping]] = ..., state: _Optional[_Union[ClusterState, str]] = ...) -> None: ...

class TerminationReason(_message.Message):
    __slots__ = ["code", "type"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    code: TerminationCode
    type: TerminationType
    def __init__(self, code: _Optional[_Union[TerminationCode, str]] = ..., type: _Optional[_Union[TerminationType, str]] = ...) -> None: ...

class ClusterListResponse(_message.Message):
    __slots__ = ["clusters"]
    CLUSTERS_FIELD_NUMBER: _ClassVar[int]
    clusters: _containers.RepeatedCompositeFieldContainer[Cluster]
    def __init__(self, clusters: _Optional[_Iterable[_Union[Cluster, _Mapping]]] = ...) -> None: ...

class Cluster(_message.Message):
    __slots__ = ["cluster_id", "cluster_name", "spark_version", "state", "custom_tags"]
    class CustomTagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    SPARK_VERSION_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_TAGS_FIELD_NUMBER: _ClassVar[int]
    cluster_id: str
    cluster_name: str
    spark_version: str
    state: ClusterState
    custom_tags: _containers.ScalarMap[str, str]
    def __init__(self, cluster_id: _Optional[str] = ..., cluster_name: _Optional[str] = ..., spark_version: _Optional[str] = ..., state: _Optional[_Union[ClusterState, str]] = ..., custom_tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetInstancePoolRequest(_message.Message):
    __slots__ = ["instance_pool_id"]
    INSTANCE_POOL_ID_FIELD_NUMBER: _ClassVar[int]
    instance_pool_id: str
    def __init__(self, instance_pool_id: _Optional[str] = ...) -> None: ...

class InstancePool(_message.Message):
    __slots__ = ["instance_pool_name", "node_type_id", "state", "instance_pool_id"]
    INSTANCE_POOL_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_POOL_ID_FIELD_NUMBER: _ClassVar[int]
    instance_pool_name: str
    node_type_id: str
    state: str
    instance_pool_id: str
    def __init__(self, instance_pool_name: _Optional[str] = ..., node_type_id: _Optional[str] = ..., state: _Optional[str] = ..., instance_pool_id: _Optional[str] = ...) -> None: ...

class ListInstancePoolsRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class InstancePools(_message.Message):
    __slots__ = ["instance_pools"]
    INSTANCE_POOLS_FIELD_NUMBER: _ClassVar[int]
    instance_pools: _containers.RepeatedCompositeFieldContainer[InstancePool]
    def __init__(self, instance_pools: _Optional[_Iterable[_Union[InstancePool, _Mapping]]] = ...) -> None: ...
