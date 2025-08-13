from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class StatusEntry(_message.Message):
    __slots__ = ["source_type", "raw_data_end_time", "anchor_time"]
    SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    RAW_DATA_END_TIME_FIELD_NUMBER: _ClassVar[int]
    ANCHOR_TIME_FIELD_NUMBER: _ClassVar[int]
    source_type: str
    raw_data_end_time: int
    anchor_time: int
    def __init__(self, source_type: _Optional[str] = ..., raw_data_end_time: _Optional[int] = ..., anchor_time: _Optional[int] = ...) -> None: ...
