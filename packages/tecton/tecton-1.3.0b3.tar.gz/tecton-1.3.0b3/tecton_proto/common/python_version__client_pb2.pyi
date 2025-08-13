from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class PythonVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    CLUSTER_DEFAULT: _ClassVar[PythonVersion]
    PYTHON_3_9_0: _ClassVar[PythonVersion]
    PYTHON_3_9_13: _ClassVar[PythonVersion]
CLUSTER_DEFAULT: PythonVersion
PYTHON_3_9_0: PythonVersion
PYTHON_3_9_13: PythonVersion
