from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.auditlog import metadata__client_pb2 as _metadata__client_pb2
from tecton_proto.auth import principal__client_pb2 as _principal__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServiceAccountCredentialsType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    SERVICE_ACCOUNT_CREDENTIALS_TYPE_UNSPECIFIED: _ClassVar[ServiceAccountCredentialsType]
    SERVICE_ACCOUNT_CREDENTIALS_TYPE_API_KEY: _ClassVar[ServiceAccountCredentialsType]
    SERVICE_ACCOUNT_CREDENTIALS_TYPE_OAUTH_CLIENT_CREDENTIALS: _ClassVar[ServiceAccountCredentialsType]
SERVICE_ACCOUNT_CREDENTIALS_TYPE_UNSPECIFIED: ServiceAccountCredentialsType
SERVICE_ACCOUNT_CREDENTIALS_TYPE_API_KEY: ServiceAccountCredentialsType
SERVICE_ACCOUNT_CREDENTIALS_TYPE_OAUTH_CLIENT_CREDENTIALS: ServiceAccountCredentialsType

class NewClientSecret(_message.Message):
    __slots__ = ["secret_id", "created_at", "status", "secret"]
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    SECRET_FIELD_NUMBER: _ClassVar[int]
    secret_id: str
    created_at: str
    status: str
    secret: str
    def __init__(self, secret_id: _Optional[str] = ..., created_at: _Optional[str] = ..., status: _Optional[str] = ..., secret: _Optional[str] = ...) -> None: ...

class MaskedClientSecret(_message.Message):
    __slots__ = ["secret_id", "created_at", "updated_at", "status", "masked_secret"]
    SECRET_ID_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MASKED_SECRET_FIELD_NUMBER: _ClassVar[int]
    secret_id: str
    created_at: str
    updated_at: str
    status: str
    masked_secret: str
    def __init__(self, secret_id: _Optional[str] = ..., created_at: _Optional[str] = ..., updated_at: _Optional[str] = ..., status: _Optional[str] = ..., masked_secret: _Optional[str] = ...) -> None: ...

class CreateServiceAccountRequest(_message.Message):
    __slots__ = ["name", "description", "credentials_type"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_TYPE_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    credentials_type: ServiceAccountCredentialsType
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., credentials_type: _Optional[_Union[ServiceAccountCredentialsType, str]] = ...) -> None: ...

class CreateServiceAccountResponse(_message.Message):
    __slots__ = ["id", "name", "description", "is_active", "api_key", "created_at", "credentials_type", "client_secret"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    API_KEY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_TYPE_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SECRET_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    is_active: bool
    api_key: str
    created_at: _timestamp_pb2.Timestamp
    credentials_type: ServiceAccountCredentialsType
    client_secret: str
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., is_active: bool = ..., api_key: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., credentials_type: _Optional[_Union[ServiceAccountCredentialsType, str]] = ..., client_secret: _Optional[str] = ...) -> None: ...

class ServiceAccount(_message.Message):
    __slots__ = ["id", "name", "description", "is_active", "created_by", "created_at", "credentials_type"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    CREDENTIALS_TYPE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    is_active: bool
    created_by: _principal__client_pb2.PrincipalBasic
    created_at: _timestamp_pb2.Timestamp
    credentials_type: ServiceAccountCredentialsType
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., is_active: bool = ..., created_by: _Optional[_Union[_principal__client_pb2.PrincipalBasic, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., credentials_type: _Optional[_Union[ServiceAccountCredentialsType, str]] = ...) -> None: ...

class GetServiceAccountsRequest(_message.Message):
    __slots__ = ["search", "ids"]
    SEARCH_FIELD_NUMBER: _ClassVar[int]
    IDS_FIELD_NUMBER: _ClassVar[int]
    search: str
    ids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, search: _Optional[str] = ..., ids: _Optional[_Iterable[str]] = ...) -> None: ...

class GetServiceAccountsResponse(_message.Message):
    __slots__ = ["service_accounts"]
    SERVICE_ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    service_accounts: _containers.RepeatedCompositeFieldContainer[ServiceAccount]
    def __init__(self, service_accounts: _Optional[_Iterable[_Union[ServiceAccount, _Mapping]]] = ...) -> None: ...

class UpdateServiceAccountRequest(_message.Message):
    __slots__ = ["id", "name", "description", "is_active"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    is_active: bool
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., is_active: bool = ...) -> None: ...

class UpdateServiceAccountResponse(_message.Message):
    __slots__ = ["id", "name", "description", "is_active", "created_at"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    IS_ACTIVE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    id: str
    name: str
    description: str
    is_active: bool
    created_at: _timestamp_pb2.Timestamp
    def __init__(self, id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., is_active: bool = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class DeleteServiceAccountRequest(_message.Message):
    __slots__ = ["id"]
    ID_FIELD_NUMBER: _ClassVar[int]
    id: str
    def __init__(self, id: _Optional[str] = ...) -> None: ...

class DeleteServiceAccountResponse(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
