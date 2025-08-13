from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class FrameworkVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNSPECIFIED: _ClassVar[FrameworkVersion]
    FWV3: _ClassVar[FrameworkVersion]
    FWV5: _ClassVar[FrameworkVersion]
    FWV6: _ClassVar[FrameworkVersion]
UNSPECIFIED: FrameworkVersion
FWV3: FrameworkVersion
FWV5: FrameworkVersion
FWV6: FrameworkVersion
