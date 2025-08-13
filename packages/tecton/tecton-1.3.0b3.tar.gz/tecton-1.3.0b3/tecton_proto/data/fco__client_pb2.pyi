from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.data import entity__client_pb2 as _entity__client_pb2
from tecton_proto.data import feature_service__client_pb2 as _feature_service__client_pb2
from tecton_proto.data import feature_view__client_pb2 as _feature_view__client_pb2
from tecton_proto.data import resource_provider__client_pb2 as _resource_provider__client_pb2
from tecton_proto.data import server_group__client_pb2 as _server_group__client_pb2
from tecton_proto.data import transformation__client_pb2 as _transformation__client_pb2
from tecton_proto.data import virtual_data_source__client_pb2 as _virtual_data_source__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Fco(_message.Message):
    __slots__ = ["virtual_data_source", "entity", "feature_view", "feature_service", "transformation", "server_group", "resource_provider"]
    VIRTUAL_DATA_SOURCE_FIELD_NUMBER: _ClassVar[int]
    ENTITY_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_FIELD_NUMBER: _ClassVar[int]
    TRANSFORMATION_FIELD_NUMBER: _ClassVar[int]
    SERVER_GROUP_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_PROVIDER_FIELD_NUMBER: _ClassVar[int]
    virtual_data_source: _virtual_data_source__client_pb2.VirtualDataSource
    entity: _entity__client_pb2.Entity
    feature_view: _feature_view__client_pb2.FeatureView
    feature_service: _feature_service__client_pb2.FeatureService
    transformation: _transformation__client_pb2.Transformation
    server_group: _server_group__client_pb2.ServerGroup
    resource_provider: _resource_provider__client_pb2.ResourceProvider
    def __init__(self, virtual_data_source: _Optional[_Union[_virtual_data_source__client_pb2.VirtualDataSource, _Mapping]] = ..., entity: _Optional[_Union[_entity__client_pb2.Entity, _Mapping]] = ..., feature_view: _Optional[_Union[_feature_view__client_pb2.FeatureView, _Mapping]] = ..., feature_service: _Optional[_Union[_feature_service__client_pb2.FeatureService, _Mapping]] = ..., transformation: _Optional[_Union[_transformation__client_pb2.Transformation, _Mapping]] = ..., server_group: _Optional[_Union[_server_group__client_pb2.ServerGroup, _Mapping]] = ..., resource_provider: _Optional[_Union[_resource_provider__client_pb2.ResourceProvider, _Mapping]] = ...) -> None: ...

class FcoContainer(_message.Message):
    __slots__ = ["root_ids", "fcos", "workspace", "workspace_state_id"]
    ROOT_IDS_FIELD_NUMBER: _ClassVar[int]
    FCOS_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_STATE_ID_FIELD_NUMBER: _ClassVar[int]
    root_ids: _containers.RepeatedCompositeFieldContainer[_id__client_pb2.Id]
    fcos: _containers.RepeatedCompositeFieldContainer[Fco]
    workspace: str
    workspace_state_id: _id__client_pb2.Id
    def __init__(self, root_ids: _Optional[_Iterable[_Union[_id__client_pb2.Id, _Mapping]]] = ..., fcos: _Optional[_Iterable[_Union[Fco, _Mapping]]] = ..., workspace: _Optional[str] = ..., workspace_state_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ...) -> None: ...
