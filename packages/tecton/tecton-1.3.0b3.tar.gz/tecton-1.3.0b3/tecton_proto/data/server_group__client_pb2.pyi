from tecton_proto.common import container_image__client_pb2 as _container_image__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import scaling_config__client_pb2 as _scaling_config__client_pb2
from tecton_proto.common import server_group_type__client_pb2 as _server_group_type__client_pb2
from tecton_proto.data import fco_metadata__client_pb2 as _fco_metadata__client_pb2
from tecton_proto.validation import validator__client_pb2 as _validator__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServerGroup(_message.Message):
    __slots__ = ["server_group_id", "fco_metadata", "type", "transform_server_group", "feature_server_group", "options", "validation_args", "autoscaling_config", "provisioned_scaling_config"]
    class OptionsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SERVER_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    FCO_METADATA_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_SERVER_GROUP_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVER_GROUP_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_ARGS_FIELD_NUMBER: _ClassVar[int]
    AUTOSCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_SCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    server_group_id: _id__client_pb2.Id
    fco_metadata: _fco_metadata__client_pb2.FcoMetadata
    type: _server_group_type__client_pb2.ServerGroupType
    transform_server_group: TransformServerGroup
    feature_server_group: FeatureServerGroup
    options: _containers.ScalarMap[str, str]
    validation_args: _validator__client_pb2.ServerGroupValidationArgs
    autoscaling_config: _scaling_config__client_pb2.AutoscalingConfig
    provisioned_scaling_config: _scaling_config__client_pb2.ProvisionedScalingConfig
    def __init__(self, server_group_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., fco_metadata: _Optional[_Union[_fco_metadata__client_pb2.FcoMetadata, _Mapping]] = ..., type: _Optional[_Union[_server_group_type__client_pb2.ServerGroupType, str]] = ..., transform_server_group: _Optional[_Union[TransformServerGroup, _Mapping]] = ..., feature_server_group: _Optional[_Union[FeatureServerGroup, _Mapping]] = ..., options: _Optional[_Mapping[str, str]] = ..., validation_args: _Optional[_Union[_validator__client_pb2.ServerGroupValidationArgs, _Mapping]] = ..., autoscaling_config: _Optional[_Union[_scaling_config__client_pb2.AutoscalingConfig, _Mapping]] = ..., provisioned_scaling_config: _Optional[_Union[_scaling_config__client_pb2.ProvisionedScalingConfig, _Mapping]] = ...) -> None: ...

class TransformServerGroup(_message.Message):
    __slots__ = ["environment_id", "environment_name", "image_info"]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_NAME_FIELD_NUMBER: _ClassVar[int]
    IMAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    environment_name: str
    image_info: _container_image__client_pb2.ContainerImage
    def __init__(self, environment_id: _Optional[str] = ..., environment_name: _Optional[str] = ..., image_info: _Optional[_Union[_container_image__client_pb2.ContainerImage, _Mapping]] = ...) -> None: ...

class FeatureServerGroup(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
