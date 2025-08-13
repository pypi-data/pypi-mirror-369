from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OnboardingStatusEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    ONBOARDING_STATUS_UNSPECIFIED: _ClassVar[OnboardingStatusEnum]
    ONBOARDING_STATUS_INCOMPLETE: _ClassVar[OnboardingStatusEnum]
    ONBOARDING_STATUS_COMPLETED: _ClassVar[OnboardingStatusEnum]

class DataPlatformSetupTaskStatusEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    TASK_STATUS_UNKNOWN: _ClassVar[DataPlatformSetupTaskStatusEnum]
    TASK_STATUS_NOT_STARTED: _ClassVar[DataPlatformSetupTaskStatusEnum]
    TASK_STATUS_RUNNING: _ClassVar[DataPlatformSetupTaskStatusEnum]
    TASK_STATUS_SUCCEEDED: _ClassVar[DataPlatformSetupTaskStatusEnum]
    TASK_STATUS_FAILED: _ClassVar[DataPlatformSetupTaskStatusEnum]
ONBOARDING_STATUS_UNSPECIFIED: OnboardingStatusEnum
ONBOARDING_STATUS_INCOMPLETE: OnboardingStatusEnum
ONBOARDING_STATUS_COMPLETED: OnboardingStatusEnum
TASK_STATUS_UNKNOWN: DataPlatformSetupTaskStatusEnum
TASK_STATUS_NOT_STARTED: DataPlatformSetupTaskStatusEnum
TASK_STATUS_RUNNING: DataPlatformSetupTaskStatusEnum
TASK_STATUS_SUCCEEDED: DataPlatformSetupTaskStatusEnum
TASK_STATUS_FAILED: DataPlatformSetupTaskStatusEnum

class OnboardingStatus(_message.Message):
    __slots__ = ["user_id", "status"]
    USER_ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    user_id: str
    status: OnboardingStatusEnum
    def __init__(self, user_id: _Optional[str] = ..., status: _Optional[_Union[OnboardingStatusEnum, str]] = ...) -> None: ...

class DataPlatformSetupTaskStatus(_message.Message):
    __slots__ = ["task_display_name", "task_status", "error_message", "details"]
    TASK_DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    TASK_STATUS_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    task_display_name: str
    task_status: DataPlatformSetupTaskStatusEnum
    error_message: str
    details: str
    def __init__(self, task_display_name: _Optional[str] = ..., task_status: _Optional[_Union[DataPlatformSetupTaskStatusEnum, str]] = ..., error_message: _Optional[str] = ..., details: _Optional[str] = ...) -> None: ...
