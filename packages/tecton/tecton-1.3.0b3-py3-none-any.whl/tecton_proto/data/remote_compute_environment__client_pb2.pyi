from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.auth import principal__client_pb2 as _principal__client_pb2
from tecton_proto.common import container_image__client_pb2 as _container_image__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class JobEnvironment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    JOB_ENVIRONMENT_UNSPECIFIED: _ClassVar[JobEnvironment]
    JOB_ENVIRONMENT_REALTIME: _ClassVar[JobEnvironment]
    JOB_ENVIRONMENT_RIFT_BATCH: _ClassVar[JobEnvironment]
    JOB_ENVIRONMENT_RIFT_STREAM: _ClassVar[JobEnvironment]

class RemoteEnvironmentStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    REMOTE_ENVIRONMENT_STATUS_PENDING: _ClassVar[RemoteEnvironmentStatus]
    REMOTE_ENVIRONMENT_STATUS_READY: _ClassVar[RemoteEnvironmentStatus]
    REMOTE_ENVIRONMENT_STATUS_ERROR: _ClassVar[RemoteEnvironmentStatus]
    REMOTE_ENVIRONMENT_STATUS_DELETING: _ClassVar[RemoteEnvironmentStatus]
    REMOTE_ENVIRONMENT_STATUS_DELETION_FAILED: _ClassVar[RemoteEnvironmentStatus]

class RemoteComputeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    REMOTE_COMPUTE_TYPE_CORE: _ClassVar[RemoteComputeType]
    REMOTE_COMPUTE_TYPE_EXTENDED: _ClassVar[RemoteComputeType]
    REMOTE_COMPUTE_TYPE_SNOWPARK_DEPRECATED_DO_NOT_USE: _ClassVar[RemoteComputeType]
    REMOTE_COMPUTE_TYPE_CUSTOM: _ClassVar[RemoteComputeType]
JOB_ENVIRONMENT_UNSPECIFIED: JobEnvironment
JOB_ENVIRONMENT_REALTIME: JobEnvironment
JOB_ENVIRONMENT_RIFT_BATCH: JobEnvironment
JOB_ENVIRONMENT_RIFT_STREAM: JobEnvironment
REMOTE_ENVIRONMENT_STATUS_PENDING: RemoteEnvironmentStatus
REMOTE_ENVIRONMENT_STATUS_READY: RemoteEnvironmentStatus
REMOTE_ENVIRONMENT_STATUS_ERROR: RemoteEnvironmentStatus
REMOTE_ENVIRONMENT_STATUS_DELETING: RemoteEnvironmentStatus
REMOTE_ENVIRONMENT_STATUS_DELETION_FAILED: RemoteEnvironmentStatus
REMOTE_COMPUTE_TYPE_CORE: RemoteComputeType
REMOTE_COMPUTE_TYPE_EXTENDED: RemoteComputeType
REMOTE_COMPUTE_TYPE_SNOWPARK_DEPRECATED_DO_NOT_USE: RemoteComputeType
REMOTE_COMPUTE_TYPE_CUSTOM: RemoteComputeType

class RemoteComputeEnvironment(_message.Message):
    __slots__ = ["id", "name", "type", "status", "image_info", "provisioned_image_info", "created_at", "updated_at", "created_by", "created_by_principal", "description", "python_version", "requirements", "resolved_requirements", "s3_wheels_location", "feature_services", "realtime_job_environment", "rift_batch_job_environment", "supported_job_environments", "sdk_version", "status_details", "deprecated"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    IMAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_IMAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PYTHON_VERSION_FIELD_NUMBER: _ClassVar[int]
    REQUIREMENTS_FIELD_NUMBER: _ClassVar[int]
    RESOLVED_REQUIREMENTS_FIELD_NUMBER: _ClassVar[int]
    S3_WHEELS_LOCATION_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICES_FIELD_NUMBER: _ClassVar[int]
    REALTIME_JOB_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    RIFT_BATCH_JOB_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_JOB_ENVIRONMENTS_FIELD_NUMBER: _ClassVar[int]
    SDK_VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_DETAILS_FIELD_NUMBER: _ClassVar[int]
    DEPRECATED_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    type: RemoteComputeType
    status: RemoteEnvironmentStatus
    image_info: _container_image__client_pb2.ContainerImage
    provisioned_image_info: _container_image__client_pb2.ContainerImage
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    created_by: _principal__client_pb2.Principal
    created_by_principal: _principal__client_pb2.PrincipalBasic
    description: str
    python_version: str
    requirements: str
    resolved_requirements: str
    s3_wheels_location: str
    feature_services: _containers.RepeatedCompositeFieldContainer[DependentFeatureService]
    realtime_job_environment: RealtimeEnvironment
    rift_batch_job_environment: RiftBatchEnvironment
    supported_job_environments: _containers.RepeatedScalarFieldContainer[JobEnvironment]
    sdk_version: str
    status_details: str
    deprecated: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., type: _Optional[_Union[RemoteComputeType, str]] = ..., status: _Optional[_Union[RemoteEnvironmentStatus, str]] = ..., image_info: _Optional[_Union[_container_image__client_pb2.ContainerImage, _Mapping]] = ..., provisioned_image_info: _Optional[_Union[_container_image__client_pb2.ContainerImage, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_by: _Optional[_Union[_principal__client_pb2.Principal, _Mapping]] = ..., created_by_principal: _Optional[_Union[_principal__client_pb2.PrincipalBasic, _Mapping]] = ..., description: _Optional[str] = ..., python_version: _Optional[str] = ..., requirements: _Optional[str] = ..., resolved_requirements: _Optional[str] = ..., s3_wheels_location: _Optional[str] = ..., feature_services: _Optional[_Iterable[_Union[DependentFeatureService, _Mapping]]] = ..., realtime_job_environment: _Optional[_Union[RealtimeEnvironment, _Mapping]] = ..., rift_batch_job_environment: _Optional[_Union[RiftBatchEnvironment, _Mapping]] = ..., supported_job_environments: _Optional[_Iterable[_Union[JobEnvironment, str]]] = ..., sdk_version: _Optional[str] = ..., status_details: _Optional[str] = ..., deprecated: bool = ...) -> None: ...

class RealtimeEnvironment(_message.Message):
    __slots__ = ["tecton_transform_runtime_version", "image_info", "provisioned_image_info", "remote_function_uri", "feature_services", "online_provisioned"]
    TECTON_TRANSFORM_RUNTIME_VERSION_FIELD_NUMBER: _ClassVar[int]
    IMAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_IMAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FUNCTION_URI_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICES_FIELD_NUMBER: _ClassVar[int]
    ONLINE_PROVISIONED_FIELD_NUMBER: _ClassVar[int]
    tecton_transform_runtime_version: str
    image_info: _container_image__client_pb2.ContainerImage
    provisioned_image_info: _container_image__client_pb2.ContainerImage
    remote_function_uri: str
    feature_services: _containers.RepeatedCompositeFieldContainer[DependentFeatureService]
    online_provisioned: bool
    def __init__(self, tecton_transform_runtime_version: _Optional[str] = ..., image_info: _Optional[_Union[_container_image__client_pb2.ContainerImage, _Mapping]] = ..., provisioned_image_info: _Optional[_Union[_container_image__client_pb2.ContainerImage, _Mapping]] = ..., remote_function_uri: _Optional[str] = ..., feature_services: _Optional[_Iterable[_Union[DependentFeatureService, _Mapping]]] = ..., online_provisioned: bool = ...) -> None: ...

class RiftBatchEnvironment(_message.Message):
    __slots__ = ["tecton_materialization_runtime_version", "image_info", "cluster_environment_build_id"]
    TECTON_MATERIALIZATION_RUNTIME_VERSION_FIELD_NUMBER: _ClassVar[int]
    IMAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_ENVIRONMENT_BUILD_ID_FIELD_NUMBER: _ClassVar[int]
    tecton_materialization_runtime_version: str
    image_info: _container_image__client_pb2.ContainerImage
    cluster_environment_build_id: str
    def __init__(self, tecton_materialization_runtime_version: _Optional[str] = ..., image_info: _Optional[_Union[_container_image__client_pb2.ContainerImage, _Mapping]] = ..., cluster_environment_build_id: _Optional[str] = ...) -> None: ...

class RemoteEnvironmentUploadInfo(_message.Message):
    __slots__ = ["environment_id", "s3_upload_info"]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    S3_UPLOAD_INFO_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    s3_upload_info: S3UploadInfo
    def __init__(self, environment_id: _Optional[str] = ..., s3_upload_info: _Optional[_Union[S3UploadInfo, _Mapping]] = ...) -> None: ...

class ObjectStoreUploadPart(_message.Message):
    __slots__ = ["s3_upload_part"]
    S3_UPLOAD_PART_FIELD_NUMBER: _ClassVar[int]
    s3_upload_part: S3UploadPart
    def __init__(self, s3_upload_part: _Optional[_Union[S3UploadPart, _Mapping]] = ...) -> None: ...

class S3UploadInfo(_message.Message):
    __slots__ = ["upload_id", "upload_parts"]
    UPLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_PARTS_FIELD_NUMBER: _ClassVar[int]
    upload_id: str
    upload_parts: _containers.RepeatedCompositeFieldContainer[S3UploadPart]
    def __init__(self, upload_id: _Optional[str] = ..., upload_parts: _Optional[_Iterable[_Union[S3UploadPart, _Mapping]]] = ...) -> None: ...

class S3UploadPart(_message.Message):
    __slots__ = ["parent_upload_id", "part_number", "e_tag", "upload_url"]
    PARENT_UPLOAD_ID_FIELD_NUMBER: _ClassVar[int]
    PART_NUMBER_FIELD_NUMBER: _ClassVar[int]
    E_TAG_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_URL_FIELD_NUMBER: _ClassVar[int]
    parent_upload_id: str
    part_number: int
    e_tag: str
    upload_url: str
    def __init__(self, parent_upload_id: _Optional[str] = ..., part_number: _Optional[int] = ..., e_tag: _Optional[str] = ..., upload_url: _Optional[str] = ...) -> None: ...

class DependentFeatureService(_message.Message):
    __slots__ = ["workspace_name", "feature_service_name"]
    WORKSPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVICE_NAME_FIELD_NUMBER: _ClassVar[int]
    workspace_name: str
    feature_service_name: str
    def __init__(self, workspace_name: _Optional[str] = ..., feature_service_name: _Optional[str] = ...) -> None: ...

class DependentFeatureView(_message.Message):
    __slots__ = ["workspace_name", "feature_view_name"]
    WORKSPACE_NAME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    workspace_name: str
    feature_view_name: str
    def __init__(self, workspace_name: _Optional[str] = ..., feature_view_name: _Optional[str] = ...) -> None: ...
