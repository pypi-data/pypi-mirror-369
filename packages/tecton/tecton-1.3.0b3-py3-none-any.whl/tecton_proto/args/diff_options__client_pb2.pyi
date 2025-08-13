from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UpdateStrategy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    RECREATE: _ClassVar[UpdateStrategy]
    INPLACE: _ClassVar[UpdateStrategy]
    INPLACE_ON_ADD: _ClassVar[UpdateStrategy]
    ONE_WAY_INPLACE_ON_ADD: _ClassVar[UpdateStrategy]
    INPLACE_ON_REMOVE: _ClassVar[UpdateStrategy]
    PASSIVE: _ClassVar[UpdateStrategy]
    RECREATE_UNLESS_SUPPRESSED: _ClassVar[UpdateStrategy]
    RECREATE_UNLESS_SUPPRESSED_INVALIDATE_CHECKPOINTS: _ClassVar[UpdateStrategy]
    RECREATE_UNLESS_SUPPRESSED_RESTART_STREAM: _ClassVar[UpdateStrategy]

class FcoPropertyRenderingType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    FCO_PROPERTY_RENDERING_TYPE_UNSPECIFIED: _ClassVar[FcoPropertyRenderingType]
    FCO_PROPERTY_RENDERING_TYPE_PLAIN_TEXT: _ClassVar[FcoPropertyRenderingType]
    FCO_PROPERTY_RENDERING_TYPE_PYTHON: _ClassVar[FcoPropertyRenderingType]
    FCO_PROPERTY_RENDERING_TYPE_SQL: _ClassVar[FcoPropertyRenderingType]
    FCO_PROPERTY_RENDERING_TYPE_ONLY_DECLARED: _ClassVar[FcoPropertyRenderingType]
    FCO_PROPERTY_RENDERING_TYPE_HIDDEN: _ClassVar[FcoPropertyRenderingType]
    FCO_PROPERTY_RENDERING_TYPE_REDACTED: _ClassVar[FcoPropertyRenderingType]

class CustomComparator(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    CUSTOM_COMPARATOR_UNSET: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_AGGREGATION_NAME: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_OPTION_VALUE_WITH_REDACTION: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_DISPLAY_NOTSET: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_REQUEST_SOURCE: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_STREAM_PROCESSING_MODE: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_DIFF_OVERRIDE_JOIN_KEYS_AS_MAP: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_BATCH_SCHEDULE: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_TIME_WINDOW_LEGACY: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_TIME_WINDOW: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_ONLINE_OFFLINE_ENABLED: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_OFFLINE_STORE: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_OFFLINE_STORE_LEGACY: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_PUBLISH_FEATURES: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_UNITY_CATALOG_ACCESS_MODE: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_ENTITY_JOIN_KEYS: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_FEATURE_PARAM_UPGRADE: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_TIMESTAMP_FIELD: _ClassVar[CustomComparator]
    CUSTOM_COMPARATOR_FILTERED_SOURCE: _ClassVar[CustomComparator]
RECREATE: UpdateStrategy
INPLACE: UpdateStrategy
INPLACE_ON_ADD: UpdateStrategy
ONE_WAY_INPLACE_ON_ADD: UpdateStrategy
INPLACE_ON_REMOVE: UpdateStrategy
PASSIVE: UpdateStrategy
RECREATE_UNLESS_SUPPRESSED: UpdateStrategy
RECREATE_UNLESS_SUPPRESSED_INVALIDATE_CHECKPOINTS: UpdateStrategy
RECREATE_UNLESS_SUPPRESSED_RESTART_STREAM: UpdateStrategy
FCO_PROPERTY_RENDERING_TYPE_UNSPECIFIED: FcoPropertyRenderingType
FCO_PROPERTY_RENDERING_TYPE_PLAIN_TEXT: FcoPropertyRenderingType
FCO_PROPERTY_RENDERING_TYPE_PYTHON: FcoPropertyRenderingType
FCO_PROPERTY_RENDERING_TYPE_SQL: FcoPropertyRenderingType
FCO_PROPERTY_RENDERING_TYPE_ONLY_DECLARED: FcoPropertyRenderingType
FCO_PROPERTY_RENDERING_TYPE_HIDDEN: FcoPropertyRenderingType
FCO_PROPERTY_RENDERING_TYPE_REDACTED: FcoPropertyRenderingType
CUSTOM_COMPARATOR_UNSET: CustomComparator
CUSTOM_COMPARATOR_AGGREGATION_NAME: CustomComparator
CUSTOM_COMPARATOR_OPTION_VALUE_WITH_REDACTION: CustomComparator
CUSTOM_COMPARATOR_DISPLAY_NOTSET: CustomComparator
CUSTOM_COMPARATOR_REQUEST_SOURCE: CustomComparator
CUSTOM_COMPARATOR_STREAM_PROCESSING_MODE: CustomComparator
CUSTOM_COMPARATOR_DIFF_OVERRIDE_JOIN_KEYS_AS_MAP: CustomComparator
CUSTOM_COMPARATOR_BATCH_SCHEDULE: CustomComparator
CUSTOM_COMPARATOR_TIME_WINDOW_LEGACY: CustomComparator
CUSTOM_COMPARATOR_TIME_WINDOW: CustomComparator
CUSTOM_COMPARATOR_ONLINE_OFFLINE_ENABLED: CustomComparator
CUSTOM_COMPARATOR_OFFLINE_STORE: CustomComparator
CUSTOM_COMPARATOR_OFFLINE_STORE_LEGACY: CustomComparator
CUSTOM_COMPARATOR_PUBLISH_FEATURES: CustomComparator
CUSTOM_COMPARATOR_UNITY_CATALOG_ACCESS_MODE: CustomComparator
CUSTOM_COMPARATOR_ENTITY_JOIN_KEYS: CustomComparator
CUSTOM_COMPARATOR_FEATURE_PARAM_UPGRADE: CustomComparator
CUSTOM_COMPARATOR_TIMESTAMP_FIELD: CustomComparator
CUSTOM_COMPARATOR_FILTERED_SOURCE: CustomComparator
DIFF_OPTIONS_FIELD_NUMBER: _ClassVar[int]
diff_options: _descriptor.FieldDescriptor

class FieldRenameConfig(_message.Message):
    __slots__ = ["former_name", "cutover_version"]
    FORMER_NAME_FIELD_NUMBER: _ClassVar[int]
    CUTOVER_VERSION_FIELD_NUMBER: _ClassVar[int]
    former_name: str
    cutover_version: str
    def __init__(self, former_name: _Optional[str] = ..., cutover_version: _Optional[str] = ...) -> None: ...

class DiffOptions(_message.Message):
    __slots__ = ["update", "hide_path", "rendering_type", "custom_comparator", "rename"]
    UPDATE_FIELD_NUMBER: _ClassVar[int]
    HIDE_PATH_FIELD_NUMBER: _ClassVar[int]
    RENDERING_TYPE_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_COMPARATOR_FIELD_NUMBER: _ClassVar[int]
    RENAME_FIELD_NUMBER: _ClassVar[int]
    update: UpdateStrategy
    hide_path: bool
    rendering_type: FcoPropertyRenderingType
    custom_comparator: CustomComparator
    rename: FieldRenameConfig
    def __init__(self, update: _Optional[_Union[UpdateStrategy, str]] = ..., hide_path: bool = ..., rendering_type: _Optional[_Union[FcoPropertyRenderingType, str]] = ..., custom_comparator: _Optional[_Union[CustomComparator, str]] = ..., rename: _Optional[_Union[FieldRenameConfig, _Mapping]] = ...) -> None: ...
