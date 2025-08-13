from tecton_proto.args import feature_service__client_pb2 as _feature_service__client_pb2
from tecton_proto.common import data_type__client_pb2 as _data_type__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.data import fco_metadata__client_pb2 as _fco_metadata__client_pb2
from tecton_proto.data import realtime_compute__client_pb2 as _realtime_compute__client_pb2
from tecton_proto.data import server_group__client_pb2 as _server_group__client_pb2
from tecton_proto.validation import validator__client_pb2 as _validator__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JoinKeyBindingType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    JOIN_KEY_BINDING_TYPE_UNSPECIFIED: _ClassVar[JoinKeyBindingType]
    JOIN_KEY_BINDING_TYPE_BOUND: _ClassVar[JoinKeyBindingType]
    JOIN_KEY_BINDING_TYPE_WILDCARD: _ClassVar[JoinKeyBindingType]
JOIN_KEY_BINDING_TYPE_UNSPECIFIED: JoinKeyBindingType
JOIN_KEY_BINDING_TYPE_BOUND: JoinKeyBindingType
JOIN_KEY_BINDING_TYPE_WILDCARD: JoinKeyBindingType

class FeatureService(_message.Message):
    __slots__ = ["feature_service_id", "feature_set_items", "fco_metadata", "online_serving_enabled", "logging", "validation_args", "realtime_environment", "enable_online_caching", "transform_server_group", "feature_server_group", "transform_server_group_name", "transform_server_group_id", "options"]
    class OptionsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    FEATURE_SERVICE_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SET_ITEMS_FIELD_NUMBER: _ClassVar[int]
    FCO_METADATA_FIELD_NUMBER: _ClassVar[int]
    ONLINE_SERVING_ENABLED_FIELD_NUMBER: _ClassVar[int]
    LOGGING_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_ARGS_FIELD_NUMBER: _ClassVar[int]
    REALTIME_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    ENABLE_ONLINE_CACHING_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_SERVER_GROUP_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVER_GROUP_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_SERVER_GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_SERVER_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    feature_service_id: _id__client_pb2.Id
    feature_set_items: _containers.RepeatedCompositeFieldContainer[FeatureSetItem]
    fco_metadata: _fco_metadata__client_pb2.FcoMetadata
    online_serving_enabled: bool
    logging: _feature_service__client_pb2.LoggingConfigArgs
    validation_args: _validator__client_pb2.FeatureServiceValidationArgs
    realtime_environment: _realtime_compute__client_pb2.OnlineComputeConfig
    enable_online_caching: bool
    transform_server_group: _server_group__client_pb2.ServerGroup
    feature_server_group: _server_group__client_pb2.ServerGroup
    transform_server_group_name: str
    transform_server_group_id: _id__client_pb2.Id
    options: _containers.ScalarMap[str, str]
    def __init__(self, feature_service_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., feature_set_items: _Optional[_Iterable[_Union[FeatureSetItem, _Mapping]]] = ..., fco_metadata: _Optional[_Union[_fco_metadata__client_pb2.FcoMetadata, _Mapping]] = ..., online_serving_enabled: bool = ..., logging: _Optional[_Union[_feature_service__client_pb2.LoggingConfigArgs, _Mapping]] = ..., validation_args: _Optional[_Union[_validator__client_pb2.FeatureServiceValidationArgs, _Mapping]] = ..., realtime_environment: _Optional[_Union[_realtime_compute__client_pb2.OnlineComputeConfig, _Mapping]] = ..., enable_online_caching: bool = ..., transform_server_group: _Optional[_Union[_server_group__client_pb2.ServerGroup, _Mapping]] = ..., feature_server_group: _Optional[_Union[_server_group__client_pb2.ServerGroup, _Mapping]] = ..., transform_server_group_name: _Optional[str] = ..., transform_server_group_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., options: _Optional[_Mapping[str, str]] = ...) -> None: ...

class JoinKeyComponent(_message.Message):
    __slots__ = ["spine_column_name", "binding_type", "data_type"]
    SPINE_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    BINDING_TYPE_FIELD_NUMBER: _ClassVar[int]
    DATA_TYPE_FIELD_NUMBER: _ClassVar[int]
    spine_column_name: str
    binding_type: JoinKeyBindingType
    data_type: _data_type__client_pb2.DataType
    def __init__(self, spine_column_name: _Optional[str] = ..., binding_type: _Optional[_Union[JoinKeyBindingType, str]] = ..., data_type: _Optional[_Union[_data_type__client_pb2.DataType, _Mapping]] = ...) -> None: ...

class JoinKeyTemplate(_message.Message):
    __slots__ = ["components"]
    COMPONENTS_FIELD_NUMBER: _ClassVar[int]
    components: _containers.RepeatedCompositeFieldContainer[JoinKeyComponent]
    def __init__(self, components: _Optional[_Iterable[_Union[JoinKeyComponent, _Mapping]]] = ...) -> None: ...

class FeatureSetItem(_message.Message):
    __slots__ = ["feature_view_id", "join_configuration_items", "namespace", "feature_columns"]
    FEATURE_VIEW_ID_FIELD_NUMBER: _ClassVar[int]
    JOIN_CONFIGURATION_ITEMS_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    feature_view_id: _id__client_pb2.Id
    join_configuration_items: _containers.RepeatedCompositeFieldContainer[JoinConfigurationItem]
    namespace: str
    feature_columns: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, feature_view_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., join_configuration_items: _Optional[_Iterable[_Union[JoinConfigurationItem, _Mapping]]] = ..., namespace: _Optional[str] = ..., feature_columns: _Optional[_Iterable[str]] = ...) -> None: ...

class JoinConfigurationItem(_message.Message):
    __slots__ = ["spine_column_name", "package_column_name"]
    SPINE_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    PACKAGE_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    spine_column_name: str
    package_column_name: str
    def __init__(self, spine_column_name: _Optional[str] = ..., package_column_name: _Optional[str] = ...) -> None: ...
