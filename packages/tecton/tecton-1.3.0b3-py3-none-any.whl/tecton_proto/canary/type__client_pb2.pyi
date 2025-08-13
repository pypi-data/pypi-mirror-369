from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class CanaryType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    CANARY_TYPE_UNSPECIFIED: _ClassVar[CanaryType]
    CANARY_TYPE_BASE: _ClassVar[CanaryType]
    CANARY_TYPE_NEW: _ClassVar[CanaryType]
CANARY_TYPE_UNSPECIFIED: CanaryType
CANARY_TYPE_BASE: CanaryType
CANARY_TYPE_NEW: CanaryType
