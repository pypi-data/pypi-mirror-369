from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.auditlog import metadata__client_pb2 as _metadata__client_pb2
from tecton_proto.auth import service__client_pb2 as _service__client_pb2
from tecton_proto.common import server_group_status__client_pb2 as _server_group_status__client_pb2
from tecton_proto.common import server_group_type__client_pb2 as _server_group_type__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNSPECIFIED: _ClassVar[Status]
    READY: _ClassVar[Status]
    PENDING: _ClassVar[Status]
    CREATING: _ClassVar[Status]
    UPDATING: _ClassVar[Status]
    DELETING: _ClassVar[Status]
    ERROR: _ClassVar[Status]
UNSPECIFIED: Status
READY: Status
PENDING: Status
CREATING: Status
UPDATING: Status
DELETING: Status
ERROR: Status

class ListServerGroupsRequest(_message.Message):
    __slots__ = ["workspace", "type"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    type: _server_group_type__client_pb2.ServerGroupType
    def __init__(self, workspace: _Optional[str] = ..., type: _Optional[_Union[_server_group_type__client_pb2.ServerGroupType, str]] = ...) -> None: ...

class ListServerGroupsResponse(_message.Message):
    __slots__ = ["server_groups"]
    SERVER_GROUPS_FIELD_NUMBER: _ClassVar[int]
    server_groups: _containers.RepeatedCompositeFieldContainer[ServerGroupInfo]
    def __init__(self, server_groups: _Optional[_Iterable[_Union[ServerGroupInfo, _Mapping]]] = ...) -> None: ...

class GetServerGroupRequest(_message.Message):
    __slots__ = ["workspace", "server_group_name"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    SERVER_GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    server_group_name: str
    def __init__(self, workspace: _Optional[str] = ..., server_group_name: _Optional[str] = ...) -> None: ...

class GetServerGroupResponse(_message.Message):
    __slots__ = ["server_group"]
    SERVER_GROUP_FIELD_NUMBER: _ClassVar[int]
    server_group: ServerGroupInfo
    def __init__(self, server_group: _Optional[_Union[ServerGroupInfo, _Mapping]] = ...) -> None: ...

class ServerGroupInfo(_message.Message):
    __slots__ = ["server_group_id", "name", "type", "description", "created_at", "owner", "last_modified_by", "tags", "desired_config", "current_config", "status", "status_details", "environment"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SERVER_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    LAST_MODIFIED_BY_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    DESIRED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CURRENT_CONFIG_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_DETAILS_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    server_group_id: str
    name: str
    type: _server_group_type__client_pb2.ServerGroupType
    description: str
    created_at: _timestamp_pb2.Timestamp
    owner: str
    last_modified_by: str
    tags: _containers.ScalarMap[str, str]
    desired_config: ServerGroupScalingConfig
    current_config: ServerGroupScalingConfig
    status: _server_group_status__client_pb2.ServerGroupStatus
    status_details: str
    environment: str
    def __init__(self, server_group_id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[_Union[_server_group_type__client_pb2.ServerGroupType, str]] = ..., description: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., owner: _Optional[str] = ..., last_modified_by: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ..., desired_config: _Optional[_Union[ServerGroupScalingConfig, _Mapping]] = ..., current_config: _Optional[_Union[ServerGroupScalingConfig, _Mapping]] = ..., status: _Optional[_Union[_server_group_status__client_pb2.ServerGroupStatus, str]] = ..., status_details: _Optional[str] = ..., environment: _Optional[str] = ...) -> None: ...

class ServerGroupScalingConfig(_message.Message):
    __slots__ = ["min_nodes", "max_nodes", "desired_nodes", "autoscaling_enabled", "last_updated_at", "workspace_state_id"]
    MIN_NODES_FIELD_NUMBER: _ClassVar[int]
    MAX_NODES_FIELD_NUMBER: _ClassVar[int]
    DESIRED_NODES_FIELD_NUMBER: _ClassVar[int]
    AUTOSCALING_ENABLED_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_STATE_ID_FIELD_NUMBER: _ClassVar[int]
    min_nodes: int
    max_nodes: int
    desired_nodes: int
    autoscaling_enabled: bool
    last_updated_at: _timestamp_pb2.Timestamp
    workspace_state_id: str
    def __init__(self, min_nodes: _Optional[int] = ..., max_nodes: _Optional[int] = ..., desired_nodes: _Optional[int] = ..., autoscaling_enabled: bool = ..., last_updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., workspace_state_id: _Optional[str] = ...) -> None: ...

class GetRealtimeLogsRequest(_message.Message):
    __slots__ = ["transform_server_group_id", "start", "end", "tail_log_count"]
    TRANSFORM_SERVER_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    START_FIELD_NUMBER: _ClassVar[int]
    END_FIELD_NUMBER: _ClassVar[int]
    TAIL_LOG_COUNT_FIELD_NUMBER: _ClassVar[int]
    transform_server_group_id: str
    start: _timestamp_pb2.Timestamp
    end: _timestamp_pb2.Timestamp
    tail_log_count: int
    def __init__(self, transform_server_group_id: _Optional[str] = ..., start: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., tail_log_count: _Optional[int] = ...) -> None: ...

class GetRealtimeLogsResponse(_message.Message):
    __slots__ = ["logs", "warnings"]
    LOGS_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    logs: _containers.RepeatedCompositeFieldContainer[RealtimeLog]
    warnings: str
    def __init__(self, logs: _Optional[_Iterable[_Union[RealtimeLog, _Mapping]]] = ..., warnings: _Optional[str] = ...) -> None: ...

class RealtimeLog(_message.Message):
    __slots__ = ["timestamp", "message", "node"]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    message: str
    node: str
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., message: _Optional[str] = ..., node: _Optional[str] = ...) -> None: ...

class TestOnlyUpdateServerStateRequest(_message.Message):
    __slots__ = ["workspace", "server_group_name"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    SERVER_GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    server_group_name: str
    def __init__(self, workspace: _Optional[str] = ..., server_group_name: _Optional[str] = ...) -> None: ...

class TestOnlyUpdateServerStateResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class TestOnlyDeleteAllServerStatesRequest(_message.Message):
    __slots__ = ["workspace"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    def __init__(self, workspace: _Optional[str] = ...) -> None: ...

class TestOnlyDeleteAllServerStatesResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class TestOnlyCreateTransformServerGroupRequest(_message.Message):
    __slots__ = ["workspace", "name", "environment", "desired_nodes"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    DESIRED_NODES_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    name: str
    environment: str
    desired_nodes: int
    def __init__(self, workspace: _Optional[str] = ..., name: _Optional[str] = ..., environment: _Optional[str] = ..., desired_nodes: _Optional[int] = ...) -> None: ...

class TestOnlyCreateTransformServerGroupResponse(_message.Message):
    __slots__ = ["transform_server_group"]
    TRANSFORM_SERVER_GROUP_FIELD_NUMBER: _ClassVar[int]
    transform_server_group: TransformServerGroup
    def __init__(self, transform_server_group: _Optional[_Union[TransformServerGroup, _Mapping]] = ...) -> None: ...

class TestOnlyCreateIngestServerGroupRequest(_message.Message):
    __slots__ = ["workspace", "name", "desired_nodes"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESIRED_NODES_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    name: str
    desired_nodes: int
    def __init__(self, workspace: _Optional[str] = ..., name: _Optional[str] = ..., desired_nodes: _Optional[int] = ...) -> None: ...

class TestOnlyCreateIngestServerGroupResponse(_message.Message):
    __slots__ = ["ingest_server_group"]
    INGEST_SERVER_GROUP_FIELD_NUMBER: _ClassVar[int]
    ingest_server_group: IngestServerGroup
    def __init__(self, ingest_server_group: _Optional[_Union[IngestServerGroup, _Mapping]] = ...) -> None: ...

class ResourceMetadata(_message.Message):
    __slots__ = ["description", "tags", "owner"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    description: str
    tags: _containers.ScalarMap[str, str]
    owner: str
    def __init__(self, description: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ..., owner: _Optional[str] = ...) -> None: ...

class AutoscalingConfig(_message.Message):
    __slots__ = ["min_nodes", "max_nodes"]
    MIN_NODES_FIELD_NUMBER: _ClassVar[int]
    MAX_NODES_FIELD_NUMBER: _ClassVar[int]
    min_nodes: int
    max_nodes: int
    def __init__(self, min_nodes: _Optional[int] = ..., max_nodes: _Optional[int] = ...) -> None: ...

class ProvisionedScalingConfig(_message.Message):
    __slots__ = ["desired_nodes"]
    DESIRED_NODES_FIELD_NUMBER: _ClassVar[int]
    desired_nodes: int
    def __init__(self, desired_nodes: _Optional[int] = ...) -> None: ...

class TransformServerGroup(_message.Message):
    __slots__ = ["workspace", "name", "id", "metadata", "autoscaling_config", "provisioned_config", "status", "status_details", "node_type", "environment", "environment_variables", "created_at", "updated_at", "pending_config"]
    class EnvironmentVariablesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class PendingConfig(_message.Message):
        __slots__ = ["autoscaling_config", "provisioned_config", "environment", "environment_variables", "node_type"]
        class EnvironmentVariablesEntry(_message.Message):
            __slots__ = ["key", "value"]
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: str
            def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
        AUTOSCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
        PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
        ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
        ENVIRONMENT_VARIABLES_FIELD_NUMBER: _ClassVar[int]
        NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
        autoscaling_config: AutoscalingConfig
        provisioned_config: ProvisionedScalingConfig
        environment: str
        environment_variables: _containers.ScalarMap[str, str]
        node_type: str
        def __init__(self, autoscaling_config: _Optional[_Union[AutoscalingConfig, _Mapping]] = ..., provisioned_config: _Optional[_Union[ProvisionedScalingConfig, _Mapping]] = ..., environment: _Optional[str] = ..., environment_variables: _Optional[_Mapping[str, str]] = ..., node_type: _Optional[str] = ...) -> None: ...
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    AUTOSCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_DETAILS_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_VARIABLES_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    PENDING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    name: str
    id: str
    metadata: ResourceMetadata
    autoscaling_config: AutoscalingConfig
    provisioned_config: ProvisionedScalingConfig
    status: Status
    status_details: str
    node_type: str
    environment: str
    environment_variables: _containers.ScalarMap[str, str]
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    pending_config: TransformServerGroup.PendingConfig
    def __init__(self, workspace: _Optional[str] = ..., name: _Optional[str] = ..., id: _Optional[str] = ..., metadata: _Optional[_Union[ResourceMetadata, _Mapping]] = ..., autoscaling_config: _Optional[_Union[AutoscalingConfig, _Mapping]] = ..., provisioned_config: _Optional[_Union[ProvisionedScalingConfig, _Mapping]] = ..., status: _Optional[_Union[Status, str]] = ..., status_details: _Optional[str] = ..., node_type: _Optional[str] = ..., environment: _Optional[str] = ..., environment_variables: _Optional[_Mapping[str, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., pending_config: _Optional[_Union[TransformServerGroup.PendingConfig, _Mapping]] = ...) -> None: ...

class CreateTransformServerGroupRequest(_message.Message):
    __slots__ = ["workspace", "name", "metadata", "autoscaling_config", "provisioned_config", "node_type", "environment", "environment_variables"]
    class EnvironmentVariablesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    AUTOSCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_VARIABLES_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    name: str
    metadata: ResourceMetadata
    autoscaling_config: AutoscalingConfig
    provisioned_config: ProvisionedScalingConfig
    node_type: str
    environment: str
    environment_variables: _containers.ScalarMap[str, str]
    def __init__(self, workspace: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[_Union[ResourceMetadata, _Mapping]] = ..., autoscaling_config: _Optional[_Union[AutoscalingConfig, _Mapping]] = ..., provisioned_config: _Optional[_Union[ProvisionedScalingConfig, _Mapping]] = ..., node_type: _Optional[str] = ..., environment: _Optional[str] = ..., environment_variables: _Optional[_Mapping[str, str]] = ...) -> None: ...

class UpdateTransformServerGroupRequest(_message.Message):
    __slots__ = ["id", "metadata", "autoscaling_config", "provisioned_config", "node_type", "environment", "environment_variables"]
    class EnvironmentVariablesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    AUTOSCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_VARIABLES_FIELD_NUMBER: _ClassVar[int]
    id: str
    metadata: ResourceMetadata
    autoscaling_config: AutoscalingConfig
    provisioned_config: ProvisionedScalingConfig
    node_type: str
    environment: str
    environment_variables: _containers.ScalarMap[str, str]
    def __init__(self, id: _Optional[str] = ..., metadata: _Optional[_Union[ResourceMetadata, _Mapping]] = ..., autoscaling_config: _Optional[_Union[AutoscalingConfig, _Mapping]] = ..., provisioned_config: _Optional[_Union[ProvisionedScalingConfig, _Mapping]] = ..., node_type: _Optional[str] = ..., environment: _Optional[str] = ..., environment_variables: _Optional[_Mapping[str, str]] = ...) -> None: ...

class DeleteTransformServerGroupRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteTransformServerGroupResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class GetTransformServerGroupRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ListTransformServerGroupsRequest(_message.Message):
    __slots__ = ["workspace"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    def __init__(self, workspace: _Optional[str] = ...) -> None: ...

class ListTransformServerGroupsResponse(_message.Message):
    __slots__ = ["transform_server_groups"]
    TRANSFORM_SERVER_GROUPS_FIELD_NUMBER: _ClassVar[int]
    transform_server_groups: _containers.RepeatedCompositeFieldContainer[TransformServerGroup]
    def __init__(self, transform_server_groups: _Optional[_Iterable[_Union[TransformServerGroup, _Mapping]]] = ...) -> None: ...

class IngestServerGroup(_message.Message):
    __slots__ = ["workspace", "name", "id", "metadata", "status", "status_details", "created_at", "updated_at", "autoscaling_config", "provisioned_config", "node_type", "pending_config"]
    class PendingConfig(_message.Message):
        __slots__ = ["autoscaling_config", "provisioned_config", "node_type"]
        AUTOSCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
        PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
        NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
        autoscaling_config: AutoscalingConfig
        provisioned_config: ProvisionedScalingConfig
        node_type: str
        def __init__(self, autoscaling_config: _Optional[_Union[AutoscalingConfig, _Mapping]] = ..., provisioned_config: _Optional[_Union[ProvisionedScalingConfig, _Mapping]] = ..., node_type: _Optional[str] = ...) -> None: ...
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_DETAILS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    AUTOSCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    PENDING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    name: str
    id: str
    metadata: ResourceMetadata
    status: Status
    status_details: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    autoscaling_config: AutoscalingConfig
    provisioned_config: ProvisionedScalingConfig
    node_type: str
    pending_config: IngestServerGroup.PendingConfig
    def __init__(self, workspace: _Optional[str] = ..., name: _Optional[str] = ..., id: _Optional[str] = ..., metadata: _Optional[_Union[ResourceMetadata, _Mapping]] = ..., status: _Optional[_Union[Status, str]] = ..., status_details: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., autoscaling_config: _Optional[_Union[AutoscalingConfig, _Mapping]] = ..., provisioned_config: _Optional[_Union[ProvisionedScalingConfig, _Mapping]] = ..., node_type: _Optional[str] = ..., pending_config: _Optional[_Union[IngestServerGroup.PendingConfig, _Mapping]] = ...) -> None: ...

class CreateIngestServerGroupRequest(_message.Message):
    __slots__ = ["workspace", "name", "metadata", "autoscaling_config", "provisioned_config", "node_type"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    AUTOSCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    name: str
    metadata: ResourceMetadata
    autoscaling_config: AutoscalingConfig
    provisioned_config: ProvisionedScalingConfig
    node_type: str
    def __init__(self, workspace: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[_Union[ResourceMetadata, _Mapping]] = ..., autoscaling_config: _Optional[_Union[AutoscalingConfig, _Mapping]] = ..., provisioned_config: _Optional[_Union[ProvisionedScalingConfig, _Mapping]] = ..., node_type: _Optional[str] = ...) -> None: ...

class DeleteIngestServerGroupRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteIngestServerGroupResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class UpdateIngestServerGroupRequest(_message.Message):
    __slots__ = ["id", "metadata", "autoscaling_config", "provisioned_config", "node_type"]
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    AUTOSCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    metadata: ResourceMetadata
    autoscaling_config: AutoscalingConfig
    provisioned_config: ProvisionedScalingConfig
    node_type: str
    def __init__(self, id: _Optional[str] = ..., metadata: _Optional[_Union[ResourceMetadata, _Mapping]] = ..., autoscaling_config: _Optional[_Union[AutoscalingConfig, _Mapping]] = ..., provisioned_config: _Optional[_Union[ProvisionedScalingConfig, _Mapping]] = ..., node_type: _Optional[str] = ...) -> None: ...

class ListIngestServerGroupsRequest(_message.Message):
    __slots__ = ["workspace"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    def __init__(self, workspace: _Optional[str] = ...) -> None: ...

class ListIngestServerGroupsResponse(_message.Message):
    __slots__ = ["ingest_server_groups"]
    INGEST_SERVER_GROUPS_FIELD_NUMBER: _ClassVar[int]
    ingest_server_groups: _containers.RepeatedCompositeFieldContainer[IngestServerGroup]
    def __init__(self, ingest_server_groups: _Optional[_Iterable[_Union[IngestServerGroup, _Mapping]]] = ...) -> None: ...

class GetIngestServerGroupRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class FeatureServerGroup(_message.Message):
    __slots__ = ["workspace", "name", "id", "metadata", "status", "status_details", "created_at", "updated_at", "autoscaling_config", "provisioned_config", "node_type", "cache_id", "pending_config"]
    class PendingConfig(_message.Message):
        __slots__ = ["autoscaling_config", "provisioned_config", "node_type", "cache_id"]
        AUTOSCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
        PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
        NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
        CACHE_ID_FIELD_NUMBER: _ClassVar[int]
        autoscaling_config: AutoscalingConfig
        provisioned_config: ProvisionedScalingConfig
        node_type: str
        cache_id: str
        def __init__(self, autoscaling_config: _Optional[_Union[AutoscalingConfig, _Mapping]] = ..., provisioned_config: _Optional[_Union[ProvisionedScalingConfig, _Mapping]] = ..., node_type: _Optional[str] = ..., cache_id: _Optional[str] = ...) -> None: ...
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_DETAILS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    AUTOSCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CACHE_ID_FIELD_NUMBER: _ClassVar[int]
    PENDING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    name: str
    id: str
    metadata: ResourceMetadata
    status: Status
    status_details: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    autoscaling_config: AutoscalingConfig
    provisioned_config: ProvisionedScalingConfig
    node_type: str
    cache_id: str
    pending_config: FeatureServerGroup.PendingConfig
    def __init__(self, workspace: _Optional[str] = ..., name: _Optional[str] = ..., id: _Optional[str] = ..., metadata: _Optional[_Union[ResourceMetadata, _Mapping]] = ..., status: _Optional[_Union[Status, str]] = ..., status_details: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., autoscaling_config: _Optional[_Union[AutoscalingConfig, _Mapping]] = ..., provisioned_config: _Optional[_Union[ProvisionedScalingConfig, _Mapping]] = ..., node_type: _Optional[str] = ..., cache_id: _Optional[str] = ..., pending_config: _Optional[_Union[FeatureServerGroup.PendingConfig, _Mapping]] = ...) -> None: ...

class CreateFeatureServerGroupRequest(_message.Message):
    __slots__ = ["workspace", "name", "metadata", "autoscaling_config", "provisioned_config", "node_type", "cache_id"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    AUTOSCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CACHE_ID_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    name: str
    metadata: ResourceMetadata
    autoscaling_config: AutoscalingConfig
    provisioned_config: ProvisionedScalingConfig
    node_type: str
    cache_id: str
    def __init__(self, workspace: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[_Union[ResourceMetadata, _Mapping]] = ..., autoscaling_config: _Optional[_Union[AutoscalingConfig, _Mapping]] = ..., provisioned_config: _Optional[_Union[ProvisionedScalingConfig, _Mapping]] = ..., node_type: _Optional[str] = ..., cache_id: _Optional[str] = ...) -> None: ...

class DeleteFeatureServerGroupRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteFeatureServerGroupResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class UpdateFeatureServerGroupRequest(_message.Message):
    __slots__ = ["id", "metadata", "autoscaling_config", "provisioned_config", "node_type", "cache_id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    AUTOSCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_FIELD_NUMBER: _ClassVar[int]
    CACHE_ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    metadata: ResourceMetadata
    autoscaling_config: AutoscalingConfig
    provisioned_config: ProvisionedScalingConfig
    node_type: str
    cache_id: str
    def __init__(self, id: _Optional[str] = ..., metadata: _Optional[_Union[ResourceMetadata, _Mapping]] = ..., autoscaling_config: _Optional[_Union[AutoscalingConfig, _Mapping]] = ..., provisioned_config: _Optional[_Union[ProvisionedScalingConfig, _Mapping]] = ..., node_type: _Optional[str] = ..., cache_id: _Optional[str] = ...) -> None: ...

class ListFeatureServerGroupsRequest(_message.Message):
    __slots__ = ["workspace"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    def __init__(self, workspace: _Optional[str] = ...) -> None: ...

class ListFeatureServerGroupsResponse(_message.Message):
    __slots__ = ["feature_server_groups"]
    FEATURE_SERVER_GROUPS_FIELD_NUMBER: _ClassVar[int]
    feature_server_groups: _containers.RepeatedCompositeFieldContainer[FeatureServerGroup]
    def __init__(self, feature_server_groups: _Optional[_Iterable[_Union[FeatureServerGroup, _Mapping]]] = ...) -> None: ...

class GetFeatureServerGroupRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class ProvisionedScalingCacheConfig(_message.Message):
    __slots__ = ["num_shards", "num_replicas_per_shard"]
    NUM_SHARDS_FIELD_NUMBER: _ClassVar[int]
    NUM_REPLICAS_PER_SHARD_FIELD_NUMBER: _ClassVar[int]
    num_shards: int
    num_replicas_per_shard: int
    def __init__(self, num_shards: _Optional[int] = ..., num_replicas_per_shard: _Optional[int] = ...) -> None: ...

class FeatureServerCache(_message.Message):
    __slots__ = ["workspace", "name", "id", "metadata", "status", "status_details", "created_at", "updated_at", "provisioned_config", "preferred_maintenance_window", "pending_config"]
    class PendingConfig(_message.Message):
        __slots__ = ["provisioned_config", "preferred_maintenance_window"]
        PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
        PREFERRED_MAINTENANCE_WINDOW_FIELD_NUMBER: _ClassVar[int]
        provisioned_config: ProvisionedScalingCacheConfig
        preferred_maintenance_window: str
        def __init__(self, provisioned_config: _Optional[_Union[ProvisionedScalingCacheConfig, _Mapping]] = ..., preferred_maintenance_window: _Optional[str] = ...) -> None: ...
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    STATUS_DETAILS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_MAINTENANCE_WINDOW_FIELD_NUMBER: _ClassVar[int]
    PENDING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    name: str
    id: str
    metadata: ResourceMetadata
    status: Status
    status_details: str
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    provisioned_config: ProvisionedScalingCacheConfig
    preferred_maintenance_window: str
    pending_config: FeatureServerCache.PendingConfig
    def __init__(self, workspace: _Optional[str] = ..., name: _Optional[str] = ..., id: _Optional[str] = ..., metadata: _Optional[_Union[ResourceMetadata, _Mapping]] = ..., status: _Optional[_Union[Status, str]] = ..., status_details: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., provisioned_config: _Optional[_Union[ProvisionedScalingCacheConfig, _Mapping]] = ..., preferred_maintenance_window: _Optional[str] = ..., pending_config: _Optional[_Union[FeatureServerCache.PendingConfig, _Mapping]] = ...) -> None: ...

class CreateFeatureServerCacheRequest(_message.Message):
    __slots__ = ["workspace", "name", "metadata", "provisioned_config", "preferred_maintenance_window"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_MAINTENANCE_WINDOW_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    name: str
    metadata: ResourceMetadata
    provisioned_config: ProvisionedScalingCacheConfig
    preferred_maintenance_window: str
    def __init__(self, workspace: _Optional[str] = ..., name: _Optional[str] = ..., metadata: _Optional[_Union[ResourceMetadata, _Mapping]] = ..., provisioned_config: _Optional[_Union[ProvisionedScalingCacheConfig, _Mapping]] = ..., preferred_maintenance_window: _Optional[str] = ...) -> None: ...

class DeleteFeatureServerCacheRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteFeatureServerCacheResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class UpdateFeatureServerCacheRequest(_message.Message):
    __slots__ = ["id", "metadata", "provisioned_config", "preferred_maintenance_window"]
    ID_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PREFERRED_MAINTENANCE_WINDOW_FIELD_NUMBER: _ClassVar[int]
    id: str
    metadata: ResourceMetadata
    provisioned_config: ProvisionedScalingCacheConfig
    preferred_maintenance_window: str
    def __init__(self, id: _Optional[str] = ..., metadata: _Optional[_Union[ResourceMetadata, _Mapping]] = ..., provisioned_config: _Optional[_Union[ProvisionedScalingCacheConfig, _Mapping]] = ..., preferred_maintenance_window: _Optional[str] = ...) -> None: ...

class ListFeatureServerCachesRequest(_message.Message):
    __slots__ = ["workspace"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    def __init__(self, workspace: _Optional[str] = ...) -> None: ...

class ListFeatureServerCachesResponse(_message.Message):
    __slots__ = ["feature_server_caches"]
    FEATURE_SERVER_CACHES_FIELD_NUMBER: _ClassVar[int]
    feature_server_caches: _containers.RepeatedCompositeFieldContainer[FeatureServerCache]
    def __init__(self, feature_server_caches: _Optional[_Iterable[_Union[FeatureServerCache, _Mapping]]] = ...) -> None: ...

class GetFeatureServerCacheRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...
