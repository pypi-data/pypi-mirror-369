from tecton_proto.auth import service__client_pb2 as _service__client_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class HttpRequest(_message.Message):
    __slots__ = ["method", "url", "body", "contentType", "contentLength"]
    METHOD_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    CONTENTTYPE_FIELD_NUMBER: _ClassVar[int]
    CONTENTLENGTH_FIELD_NUMBER: _ClassVar[int]
    method: str
    url: str
    body: bytes
    contentType: str
    contentLength: int
    def __init__(self, method: _Optional[str] = ..., url: _Optional[str] = ..., body: _Optional[bytes] = ..., contentType: _Optional[str] = ..., contentLength: _Optional[int] = ...) -> None: ...

class HttpResponseHeaders(_message.Message):
    __slots__ = ["status", "contentType", "contentLength"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CONTENTTYPE_FIELD_NUMBER: _ClassVar[int]
    CONTENTLENGTH_FIELD_NUMBER: _ClassVar[int]
    status: int
    contentType: str
    contentLength: int
    def __init__(self, status: _Optional[int] = ..., contentType: _Optional[str] = ..., contentLength: _Optional[int] = ...) -> None: ...

class HttpResponsePiece(_message.Message):
    __slots__ = ["headers", "body_piece"]
    HEADERS_FIELD_NUMBER: _ClassVar[int]
    BODY_PIECE_FIELD_NUMBER: _ClassVar[int]
    headers: HttpResponseHeaders
    body_piece: bytes
    def __init__(self, headers: _Optional[_Union[HttpResponseHeaders, _Mapping]] = ..., body_piece: _Optional[bytes] = ...) -> None: ...
