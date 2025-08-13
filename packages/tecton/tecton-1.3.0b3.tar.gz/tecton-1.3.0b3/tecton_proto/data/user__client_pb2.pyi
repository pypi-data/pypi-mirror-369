from google.protobuf import timestamp_pb2 as _timestamp_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class User(_message.Message):
    __slots__ = ["okta_id", "first_name", "last_name", "login_email", "okta_status", "created_at", "is_admin", "last_login"]
    OKTA_ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    LOGIN_EMAIL_FIELD_NUMBER: _ClassVar[int]
    OKTA_STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_ADMIN_FIELD_NUMBER: _ClassVar[int]
    LAST_LOGIN_FIELD_NUMBER: _ClassVar[int]
    okta_id: str
    first_name: str
    last_name: str
    login_email: str
    okta_status: str
    created_at: _timestamp_pb2.Timestamp
    is_admin: bool
    last_login: _timestamp_pb2.Timestamp
    def __init__(self, okta_id: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., login_email: _Optional[str] = ..., okta_status: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., is_admin: bool = ..., last_login: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
