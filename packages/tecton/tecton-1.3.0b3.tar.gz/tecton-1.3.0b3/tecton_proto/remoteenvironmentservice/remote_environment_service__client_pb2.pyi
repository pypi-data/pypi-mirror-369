from tecton_proto.auth import service__client_pb2 as _service__client_pb2
from tecton_proto.common import container_image__client_pb2 as _container_image__client_pb2
from tecton_proto.data import remote_compute_environment__client_pb2 as _remote_compute_environment__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateRemoteEnvironmentRequest(_message.Message):
    __slots__ = ["name", "description", "image_info", "id", "python_version", "requirements", "resolved_requirements", "s3_wheels_location", "transform_runtime_version", "rift_materialization_runtime_version", "sdk_version", "online_provisioned"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IMAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PYTHON_VERSION_FIELD_NUMBER: _ClassVar[int]
    REQUIREMENTS_FIELD_NUMBER: _ClassVar[int]
    RESOLVED_REQUIREMENTS_FIELD_NUMBER: _ClassVar[int]
    S3_WHEELS_LOCATION_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_RUNTIME_VERSION_FIELD_NUMBER: _ClassVar[int]
    RIFT_MATERIALIZATION_RUNTIME_VERSION_FIELD_NUMBER: _ClassVar[int]
    SDK_VERSION_FIELD_NUMBER: _ClassVar[int]
    ONLINE_PROVISIONED_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    image_info: _container_image__client_pb2.ContainerImage
    id: str
    python_version: str
    requirements: str
    resolved_requirements: str
    s3_wheels_location: str
    transform_runtime_version: str
    rift_materialization_runtime_version: str
    sdk_version: str
    online_provisioned: bool
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., image_info: _Optional[_Union[_container_image__client_pb2.ContainerImage, _Mapping]] = ..., id: _Optional[str] = ..., python_version: _Optional[str] = ..., requirements: _Optional[str] = ..., resolved_requirements: _Optional[str] = ..., s3_wheels_location: _Optional[str] = ..., transform_runtime_version: _Optional[str] = ..., rift_materialization_runtime_version: _Optional[str] = ..., sdk_version: _Optional[str] = ..., online_provisioned: bool = ...) -> None: ...

class CreateRemoteEnvironmentResponse(_message.Message):
    __slots__ = ["remote_environment"]
    REMOTE_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    remote_environment: _remote_compute_environment__client_pb2.RemoteComputeEnvironment
    def __init__(self, remote_environment: _Optional[_Union[_remote_compute_environment__client_pb2.RemoteComputeEnvironment, _Mapping]] = ...) -> None: ...

class UpdateRemoteEnvironmentRequest(_message.Message):
    __slots__ = ["id", "remote_function_version", "status"]
    ID_FIELD_NUMBER: _ClassVar[int]
    REMOTE_FUNCTION_VERSION_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    id: str
    remote_function_version: str
    status: _remote_compute_environment__client_pb2.RemoteEnvironmentStatus
    def __init__(self, id: _Optional[str] = ..., remote_function_version: _Optional[str] = ..., status: _Optional[_Union[_remote_compute_environment__client_pb2.RemoteEnvironmentStatus, str]] = ...) -> None: ...

class UpdateRemoteEnvironmentResponse(_message.Message):
    __slots__ = ["remote_environment"]
    REMOTE_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    remote_environment: _remote_compute_environment__client_pb2.RemoteComputeEnvironment
    def __init__(self, remote_environment: _Optional[_Union[_remote_compute_environment__client_pb2.RemoteComputeEnvironment, _Mapping]] = ...) -> None: ...

class DeleteRemoteEnvironmentsRequest(_message.Message):
    __slots__ = ["ids"]
    IDS_FIELD_NUMBER: _ClassVar[int]
    ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, ids: _Optional[_Iterable[str]] = ...) -> None: ...

class DeleteRemoteEnvironmentsResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ListRemoteEnvironmentsRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ListRemoteEnvironmentsResponse(_message.Message):
    __slots__ = ["remote_environments"]
    REMOTE_ENVIRONMENTS_FIELD_NUMBER: _ClassVar[int]
    remote_environments: _containers.RepeatedCompositeFieldContainer[_remote_compute_environment__client_pb2.RemoteComputeEnvironment]
    def __init__(self, remote_environments: _Optional[_Iterable[_Union[_remote_compute_environment__client_pb2.RemoteComputeEnvironment, _Mapping]]] = ...) -> None: ...

class GetRemoteEnvironmentRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class GetRemoteEnvironmentResponse(_message.Message):
    __slots__ = ["remote_environment"]
    REMOTE_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    remote_environment: _remote_compute_environment__client_pb2.RemoteComputeEnvironment
    def __init__(self, remote_environment: _Optional[_Union[_remote_compute_environment__client_pb2.RemoteComputeEnvironment, _Mapping]] = ...) -> None: ...

class GetPackagesUploadUrlRequest(_message.Message):
    __slots__ = ["environment_id", "upload_part"]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_PART_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    upload_part: _remote_compute_environment__client_pb2.ObjectStoreUploadPart
    def __init__(self, environment_id: _Optional[str] = ..., upload_part: _Optional[_Union[_remote_compute_environment__client_pb2.ObjectStoreUploadPart, _Mapping]] = ...) -> None: ...

class GetPackagesUploadUrlResponse(_message.Message):
    __slots__ = ["upload_url"]
    UPLOAD_URL_FIELD_NUMBER: _ClassVar[int]
    upload_url: str
    def __init__(self, upload_url: _Optional[str] = ...) -> None: ...

class StartPackagesUploadRequest(_message.Message):
    __slots__ = ["environment_id"]
    ENVIRONMENT_ID_FIELD_NUMBER: _ClassVar[int]
    environment_id: str
    def __init__(self, environment_id: _Optional[str] = ...) -> None: ...

class StartPackagesUploadResponse(_message.Message):
    __slots__ = ["upload_info"]
    UPLOAD_INFO_FIELD_NUMBER: _ClassVar[int]
    upload_info: _remote_compute_environment__client_pb2.RemoteEnvironmentUploadInfo
    def __init__(self, upload_info: _Optional[_Union[_remote_compute_environment__client_pb2.RemoteEnvironmentUploadInfo, _Mapping]] = ...) -> None: ...

class CompletePackagesUploadRequest(_message.Message):
    __slots__ = ["upload_info"]
    UPLOAD_INFO_FIELD_NUMBER: _ClassVar[int]
    upload_info: _remote_compute_environment__client_pb2.RemoteEnvironmentUploadInfo
    def __init__(self, upload_info: _Optional[_Union[_remote_compute_environment__client_pb2.RemoteEnvironmentUploadInfo, _Mapping]] = ...) -> None: ...

class CompletePackagesUploadResponse(_message.Message):
    __slots__ = ["storage_location"]
    STORAGE_LOCATION_FIELD_NUMBER: _ClassVar[int]
    storage_location: str
    def __init__(self, storage_location: _Optional[str] = ...) -> None: ...

class TestOnlyUpdateEnvironmentRequest(_message.Message):
    __slots__ = ["environment"]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    environment: str
    def __init__(self, environment: _Optional[str] = ...) -> None: ...

class TestOnlyUpdateEnvironmentResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class TestOnlyCreateRemoteComputeEnvironmentRequest(_message.Message):
    __slots__ = ["name", "description", "image_info", "provisioned_image_info", "transform_runtime_version", "rift_materialization_runtime_version"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IMAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_IMAGE_INFO_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_RUNTIME_VERSION_FIELD_NUMBER: _ClassVar[int]
    RIFT_MATERIALIZATION_RUNTIME_VERSION_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    image_info: _container_image__client_pb2.ContainerImage
    provisioned_image_info: _container_image__client_pb2.ContainerImage
    transform_runtime_version: str
    rift_materialization_runtime_version: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., image_info: _Optional[_Union[_container_image__client_pb2.ContainerImage, _Mapping]] = ..., provisioned_image_info: _Optional[_Union[_container_image__client_pb2.ContainerImage, _Mapping]] = ..., transform_runtime_version: _Optional[str] = ..., rift_materialization_runtime_version: _Optional[str] = ...) -> None: ...

class TestOnlyCreateRemoteComputeEnvironmentResponse(_message.Message):
    __slots__ = ["remote_environment"]
    REMOTE_ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    remote_environment: _remote_compute_environment__client_pb2.RemoteComputeEnvironment
    def __init__(self, remote_environment: _Optional[_Union[_remote_compute_environment__client_pb2.RemoteComputeEnvironment, _Mapping]] = ...) -> None: ...
