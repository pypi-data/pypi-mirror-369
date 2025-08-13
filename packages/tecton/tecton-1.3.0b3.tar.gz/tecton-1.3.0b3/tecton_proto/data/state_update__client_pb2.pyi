from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.args import diff_options__client_pb2 as _diff_options__client_pb2
from tecton_proto.args import fco_args__client_pb2 as _fco_args__client_pb2
from tecton_proto.args import repo_metadata__client_pb2 as _repo_metadata__client_pb2
from tecton_proto.auth import principal__client_pb2 as _principal__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FcoTransitionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNKNOWN: _ClassVar[FcoTransitionType]
    CREATE: _ClassVar[FcoTransitionType]
    DELETE: _ClassVar[FcoTransitionType]
    UPGRADE: _ClassVar[FcoTransitionType]
    UPDATE: _ClassVar[FcoTransitionType]
    RECREATE: _ClassVar[FcoTransitionType]
    UNCHANGED: _ClassVar[FcoTransitionType]

class FcoTransitionSideEffectStreamRestartType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    RESTART_STREAM_NONE: _ClassVar[FcoTransitionSideEffectStreamRestartType]
    RESTART_STREAM_REUSE_CHECKPOINTS: _ClassVar[FcoTransitionSideEffectStreamRestartType]
    RESTART_STREAM_CHECKPOINTS_INVALIDATED: _ClassVar[FcoTransitionSideEffectStreamRestartType]

class MaterializationTaskDiffDestination(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    MATERIALIZATION_TASK_DIFF_DESTINATION_UNSPECIFIED: _ClassVar[MaterializationTaskDiffDestination]
    MATERIALIZATION_TASK_DIFF_DESTINATION_OFFLINE: _ClassVar[MaterializationTaskDiffDestination]
    MATERIALIZATION_TASK_DIFF_DESTINATION_ONLINE: _ClassVar[MaterializationTaskDiffDestination]
    MATERIALIZATION_TASK_DIFF_DESTINATION_ONLINE_AND_OFFLINE: _ClassVar[MaterializationTaskDiffDestination]
    MATERIALIZATION_TASK_DIFF_DESTINATION_BULK_LOAD_ONLINE: _ClassVar[MaterializationTaskDiffDestination]

class IntegrationTestJobStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    JOB_STATUS_UNSPECIFIED: _ClassVar[IntegrationTestJobStatus]
    JOB_STATUS_NOT_STARTED: _ClassVar[IntegrationTestJobStatus]
    JOB_STATUS_RUNNING: _ClassVar[IntegrationTestJobStatus]
    JOB_STATUS_CANCELLED: _ClassVar[IntegrationTestJobStatus]
    JOB_STATUS_SUCCEED: _ClassVar[IntegrationTestJobStatus]
    JOB_STATUS_FAILED: _ClassVar[IntegrationTestJobStatus]

class PlanIntegrationTestSelectType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNSPECIFIED: _ClassVar[PlanIntegrationTestSelectType]
    AUTO: _ClassVar[PlanIntegrationTestSelectType]
    NONE: _ClassVar[PlanIntegrationTestSelectType]
    SELECTED_FEATURE_VIEWS: _ClassVar[PlanIntegrationTestSelectType]

class PlanStatusType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    PLAN_UNSPECIFIED: _ClassVar[PlanStatusType]
    PLAN_CREATED: _ClassVar[PlanStatusType]
    PLAN_INTEGRATION_TESTS_SKIPPED: _ClassVar[PlanStatusType]
    PLAN_INTEGRATION_TESTS_NOT_STARTED: _ClassVar[PlanStatusType]
    PLAN_INTEGRATION_TESTS_RUNNING: _ClassVar[PlanStatusType]
    PLAN_INTEGRATION_TESTS_CANCELLED: _ClassVar[PlanStatusType]
    PLAN_INTEGRATION_TESTS_SUCCEED: _ClassVar[PlanStatusType]
    PLAN_INTEGRATION_TESTS_FAILED: _ClassVar[PlanStatusType]
    PLAN_APPLIED: _ClassVar[PlanStatusType]
    PLAN_APPLY_FAILED: _ClassVar[PlanStatusType]
UNKNOWN: FcoTransitionType
CREATE: FcoTransitionType
DELETE: FcoTransitionType
UPGRADE: FcoTransitionType
UPDATE: FcoTransitionType
RECREATE: FcoTransitionType
UNCHANGED: FcoTransitionType
RESTART_STREAM_NONE: FcoTransitionSideEffectStreamRestartType
RESTART_STREAM_REUSE_CHECKPOINTS: FcoTransitionSideEffectStreamRestartType
RESTART_STREAM_CHECKPOINTS_INVALIDATED: FcoTransitionSideEffectStreamRestartType
MATERIALIZATION_TASK_DIFF_DESTINATION_UNSPECIFIED: MaterializationTaskDiffDestination
MATERIALIZATION_TASK_DIFF_DESTINATION_OFFLINE: MaterializationTaskDiffDestination
MATERIALIZATION_TASK_DIFF_DESTINATION_ONLINE: MaterializationTaskDiffDestination
MATERIALIZATION_TASK_DIFF_DESTINATION_ONLINE_AND_OFFLINE: MaterializationTaskDiffDestination
MATERIALIZATION_TASK_DIFF_DESTINATION_BULK_LOAD_ONLINE: MaterializationTaskDiffDestination
JOB_STATUS_UNSPECIFIED: IntegrationTestJobStatus
JOB_STATUS_NOT_STARTED: IntegrationTestJobStatus
JOB_STATUS_RUNNING: IntegrationTestJobStatus
JOB_STATUS_CANCELLED: IntegrationTestJobStatus
JOB_STATUS_SUCCEED: IntegrationTestJobStatus
JOB_STATUS_FAILED: IntegrationTestJobStatus
UNSPECIFIED: PlanIntegrationTestSelectType
AUTO: PlanIntegrationTestSelectType
NONE: PlanIntegrationTestSelectType
SELECTED_FEATURE_VIEWS: PlanIntegrationTestSelectType
PLAN_UNSPECIFIED: PlanStatusType
PLAN_CREATED: PlanStatusType
PLAN_INTEGRATION_TESTS_SKIPPED: PlanStatusType
PLAN_INTEGRATION_TESTS_NOT_STARTED: PlanStatusType
PLAN_INTEGRATION_TESTS_RUNNING: PlanStatusType
PLAN_INTEGRATION_TESTS_CANCELLED: PlanStatusType
PLAN_INTEGRATION_TESTS_SUCCEED: PlanStatusType
PLAN_INTEGRATION_TESTS_FAILED: PlanStatusType
PLAN_APPLIED: PlanStatusType
PLAN_APPLY_FAILED: PlanStatusType

class FcoPropertyDiff(_message.Message):
    __slots__ = ["property_name", "val_existing", "val_declared", "rendering_type", "custom_comparator"]
    PROPERTY_NAME_FIELD_NUMBER: _ClassVar[int]
    VAL_EXISTING_FIELD_NUMBER: _ClassVar[int]
    VAL_DECLARED_FIELD_NUMBER: _ClassVar[int]
    RENDERING_TYPE_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_COMPARATOR_FIELD_NUMBER: _ClassVar[int]
    property_name: str
    val_existing: str
    val_declared: str
    rendering_type: _diff_options__client_pb2.FcoPropertyRenderingType
    custom_comparator: _diff_options__client_pb2.CustomComparator
    def __init__(self, property_name: _Optional[str] = ..., val_existing: _Optional[str] = ..., val_declared: _Optional[str] = ..., rendering_type: _Optional[_Union[_diff_options__client_pb2.FcoPropertyRenderingType, str]] = ..., custom_comparator: _Optional[_Union[_diff_options__client_pb2.CustomComparator, str]] = ...) -> None: ...

class FcoTransitionSideEffects(_message.Message):
    __slots__ = ["stream_restart_type"]
    STREAM_RESTART_TYPE_FIELD_NUMBER: _ClassVar[int]
    stream_restart_type: FcoTransitionSideEffectStreamRestartType
    def __init__(self, stream_restart_type: _Optional[_Union[FcoTransitionSideEffectStreamRestartType, str]] = ...) -> None: ...

class BatchMaterializationTaskDiff(_message.Message):
    __slots__ = ["display_string", "schedule_interval", "destination"]
    DISPLAY_STRING_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    display_string: str
    schedule_interval: _duration_pb2.Duration
    destination: MaterializationTaskDiffDestination
    def __init__(self, display_string: _Optional[str] = ..., schedule_interval: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., destination: _Optional[_Union[MaterializationTaskDiffDestination, str]] = ...) -> None: ...

class StreamMaterializationTaskDiff(_message.Message):
    __slots__ = ["display_string"]
    DISPLAY_STRING_FIELD_NUMBER: _ClassVar[int]
    display_string: str
    def __init__(self, display_string: _Optional[str] = ...) -> None: ...

class BackfillMaterializationTaskDiff(_message.Message):
    __slots__ = ["display_string", "feature_start_time", "feature_end_time", "number_of_jobs", "destination"]
    DISPLAY_STRING_FIELD_NUMBER: _ClassVar[int]
    FEATURE_START_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_END_TIME_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_JOBS_FIELD_NUMBER: _ClassVar[int]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    display_string: str
    feature_start_time: _timestamp_pb2.Timestamp
    feature_end_time: _timestamp_pb2.Timestamp
    number_of_jobs: int
    destination: MaterializationTaskDiffDestination
    def __init__(self, display_string: _Optional[str] = ..., feature_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., number_of_jobs: _Optional[int] = ..., destination: _Optional[_Union[MaterializationTaskDiffDestination, str]] = ...) -> None: ...

class PlanIntegrationTestTaskDiff(_message.Message):
    __slots__ = ["display_string", "feature_view_name"]
    DISPLAY_STRING_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    display_string: str
    feature_view_name: str
    def __init__(self, display_string: _Optional[str] = ..., feature_view_name: _Optional[str] = ...) -> None: ...

class MaterializationInfo(_message.Message):
    __slots__ = ["backfill_task_diffs", "batch_task_diff", "stream_task_diff", "backfill_publish_task_diffs", "integration_test_task_diffs"]
    BACKFILL_TASK_DIFFS_FIELD_NUMBER: _ClassVar[int]
    BATCH_TASK_DIFF_FIELD_NUMBER: _ClassVar[int]
    STREAM_TASK_DIFF_FIELD_NUMBER: _ClassVar[int]
    BACKFILL_PUBLISH_TASK_DIFFS_FIELD_NUMBER: _ClassVar[int]
    INTEGRATION_TEST_TASK_DIFFS_FIELD_NUMBER: _ClassVar[int]
    backfill_task_diffs: _containers.RepeatedCompositeFieldContainer[BackfillMaterializationTaskDiff]
    batch_task_diff: BatchMaterializationTaskDiff
    stream_task_diff: StreamMaterializationTaskDiff
    backfill_publish_task_diffs: _containers.RepeatedCompositeFieldContainer[BackfillFeaturePublishTaskDiff]
    integration_test_task_diffs: _containers.RepeatedCompositeFieldContainer[PlanIntegrationTestTaskDiff]
    def __init__(self, backfill_task_diffs: _Optional[_Iterable[_Union[BackfillMaterializationTaskDiff, _Mapping]]] = ..., batch_task_diff: _Optional[_Union[BatchMaterializationTaskDiff, _Mapping]] = ..., stream_task_diff: _Optional[_Union[StreamMaterializationTaskDiff, _Mapping]] = ..., backfill_publish_task_diffs: _Optional[_Iterable[_Union[BackfillFeaturePublishTaskDiff, _Mapping]]] = ..., integration_test_task_diffs: _Optional[_Iterable[_Union[PlanIntegrationTestTaskDiff, _Mapping]]] = ...) -> None: ...

class BackfillFeaturePublishTaskDiff(_message.Message):
    __slots__ = ["display_string", "feature_start_time", "feature_end_time", "number_of_jobs"]
    DISPLAY_STRING_FIELD_NUMBER: _ClassVar[int]
    FEATURE_START_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_END_TIME_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_JOBS_FIELD_NUMBER: _ClassVar[int]
    display_string: str
    feature_start_time: _timestamp_pb2.Timestamp
    feature_end_time: _timestamp_pb2.Timestamp
    number_of_jobs: int
    def __init__(self, display_string: _Optional[str] = ..., feature_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., number_of_jobs: _Optional[int] = ...) -> None: ...

class FcoDiff(_message.Message):
    __slots__ = ["type", "transition_side_effects", "existing_args", "declared_args", "diff", "materialization_info"]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSITION_SIDE_EFFECTS_FIELD_NUMBER: _ClassVar[int]
    EXISTING_ARGS_FIELD_NUMBER: _ClassVar[int]
    DECLARED_ARGS_FIELD_NUMBER: _ClassVar[int]
    DIFF_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_INFO_FIELD_NUMBER: _ClassVar[int]
    type: FcoTransitionType
    transition_side_effects: FcoTransitionSideEffects
    existing_args: _fco_args__client_pb2.FcoArgs
    declared_args: _fco_args__client_pb2.FcoArgs
    diff: _containers.RepeatedCompositeFieldContainer[FcoPropertyDiff]
    materialization_info: MaterializationInfo
    def __init__(self, type: _Optional[_Union[FcoTransitionType, str]] = ..., transition_side_effects: _Optional[_Union[FcoTransitionSideEffects, _Mapping]] = ..., existing_args: _Optional[_Union[_fco_args__client_pb2.FcoArgs, _Mapping]] = ..., declared_args: _Optional[_Union[_fco_args__client_pb2.FcoArgs, _Mapping]] = ..., diff: _Optional[_Iterable[_Union[FcoPropertyDiff, _Mapping]]] = ..., materialization_info: _Optional[_Union[MaterializationInfo, _Mapping]] = ...) -> None: ...

class FcoFieldRef(_message.Message):
    __slots__ = ["fco_id"]
    FCO_ID_FIELD_NUMBER: _ClassVar[int]
    fco_id: _id__client_pb2.Id
    def __init__(self, fco_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ...) -> None: ...

class ValidationMessage(_message.Message):
    __slots__ = ["message", "fco_refs"]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    FCO_REFS_FIELD_NUMBER: _ClassVar[int]
    message: str
    fco_refs: _containers.RepeatedCompositeFieldContainer[FcoFieldRef]
    def __init__(self, message: _Optional[str] = ..., fco_refs: _Optional[_Iterable[_Union[FcoFieldRef, _Mapping]]] = ...) -> None: ...

class ValidationResult(_message.Message):
    __slots__ = ["errors", "warnings"]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    errors: _containers.RepeatedCompositeFieldContainer[ValidationMessage]
    warnings: _containers.RepeatedCompositeFieldContainer[ValidationMessage]
    def __init__(self, errors: _Optional[_Iterable[_Union[ValidationMessage, _Mapping]]] = ..., warnings: _Optional[_Iterable[_Union[ValidationMessage, _Mapping]]] = ...) -> None: ...

class SuccessfulPlanOutput(_message.Message):
    __slots__ = ["string_output", "json_output", "apply_warnings", "num_fcos_changed", "num_warnings", "test_summaries", "plan_url"]
    STRING_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    JSON_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    APPLY_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    NUM_FCOS_CHANGED_FIELD_NUMBER: _ClassVar[int]
    NUM_WARNINGS_FIELD_NUMBER: _ClassVar[int]
    TEST_SUMMARIES_FIELD_NUMBER: _ClassVar[int]
    PLAN_URL_FIELD_NUMBER: _ClassVar[int]
    string_output: str
    json_output: str
    apply_warnings: str
    num_fcos_changed: int
    num_warnings: int
    test_summaries: _containers.RepeatedCompositeFieldContainer[PlanIntegrationTestSummary]
    plan_url: str
    def __init__(self, string_output: _Optional[str] = ..., json_output: _Optional[str] = ..., apply_warnings: _Optional[str] = ..., num_fcos_changed: _Optional[int] = ..., num_warnings: _Optional[int] = ..., test_summaries: _Optional[_Iterable[_Union[PlanIntegrationTestSummary, _Mapping]]] = ..., plan_url: _Optional[str] = ...) -> None: ...

class IntegrationTestJobSummary(_message.Message):
    __slots__ = ["status"]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    status: IntegrationTestJobStatus
    def __init__(self, status: _Optional[_Union[IntegrationTestJobStatus, str]] = ...) -> None: ...

class PlanIntegrationTestSummary(_message.Message):
    __slots__ = ["feature_view_id", "job_summaries", "feature_view_name"]
    FEATURE_VIEW_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_SUMMARIES_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    feature_view_id: _id__client_pb2.Id
    job_summaries: _containers.RepeatedCompositeFieldContainer[IntegrationTestJobSummary]
    feature_view_name: str
    def __init__(self, feature_view_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., job_summaries: _Optional[_Iterable[_Union[IntegrationTestJobSummary, _Mapping]]] = ..., feature_view_name: _Optional[str] = ...) -> None: ...

class PlanIntegrationTestConfig(_message.Message):
    __slots__ = ["auto_apply_upon_test_success", "feature_view_names"]
    AUTO_APPLY_UPON_TEST_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NAMES_FIELD_NUMBER: _ClassVar[int]
    auto_apply_upon_test_success: bool
    feature_view_names: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, auto_apply_upon_test_success: bool = ..., feature_view_names: _Optional[_Iterable[str]] = ...) -> None: ...

class StateUpdateRequest(_message.Message):
    __slots__ = ["workspace", "fco_args", "repo_source_info", "suppress_recreates", "upgrade_all", "requested_by", "requested_by_principal", "sdk_version", "plan_integration_type", "plan_integration_config"]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    FCO_ARGS_FIELD_NUMBER: _ClassVar[int]
    REPO_SOURCE_INFO_FIELD_NUMBER: _ClassVar[int]
    SUPPRESS_RECREATES_FIELD_NUMBER: _ClassVar[int]
    UPGRADE_ALL_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_BY_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_BY_PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    SDK_VERSION_FIELD_NUMBER: _ClassVar[int]
    PLAN_INTEGRATION_TYPE_FIELD_NUMBER: _ClassVar[int]
    PLAN_INTEGRATION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    workspace: str
    fco_args: _containers.RepeatedCompositeFieldContainer[_fco_args__client_pb2.FcoArgs]
    repo_source_info: _repo_metadata__client_pb2.FeatureRepoSourceInfo
    suppress_recreates: bool
    upgrade_all: bool
    requested_by: str
    requested_by_principal: _principal__client_pb2.Principal
    sdk_version: str
    plan_integration_type: PlanIntegrationTestSelectType
    plan_integration_config: PlanIntegrationTestConfig
    def __init__(self, workspace: _Optional[str] = ..., fco_args: _Optional[_Iterable[_Union[_fco_args__client_pb2.FcoArgs, _Mapping]]] = ..., repo_source_info: _Optional[_Union[_repo_metadata__client_pb2.FeatureRepoSourceInfo, _Mapping]] = ..., suppress_recreates: bool = ..., upgrade_all: bool = ..., requested_by: _Optional[str] = ..., requested_by_principal: _Optional[_Union[_principal__client_pb2.Principal, _Mapping]] = ..., sdk_version: _Optional[str] = ..., plan_integration_type: _Optional[_Union[PlanIntegrationTestSelectType, str]] = ..., plan_integration_config: _Optional[_Union[PlanIntegrationTestConfig, _Mapping]] = ...) -> None: ...

class StateUpdateEntry(_message.Message):
    __slots__ = ["commit_id", "applied_by", "applied_by_principal", "applied_at", "workspace", "sdk_version", "created_at", "status_type", "error", "successful_plan_output", "created_by", "created_by_principal"]
    COMMIT_ID_FIELD_NUMBER: _ClassVar[int]
    APPLIED_BY_FIELD_NUMBER: _ClassVar[int]
    APPLIED_BY_PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    APPLIED_AT_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    SDK_VERSION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    STATUS_TYPE_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    SUCCESSFUL_PLAN_OUTPUT_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    commit_id: str
    applied_by: str
    applied_by_principal: _principal__client_pb2.PrincipalBasic
    applied_at: _timestamp_pb2.Timestamp
    workspace: str
    sdk_version: str
    created_at: _timestamp_pb2.Timestamp
    status_type: PlanStatusType
    error: str
    successful_plan_output: SuccessfulPlanOutput
    created_by: str
    created_by_principal: _principal__client_pb2.PrincipalBasic
    def __init__(self, commit_id: _Optional[str] = ..., applied_by: _Optional[str] = ..., applied_by_principal: _Optional[_Union[_principal__client_pb2.PrincipalBasic, _Mapping]] = ..., applied_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., workspace: _Optional[str] = ..., sdk_version: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., status_type: _Optional[_Union[PlanStatusType, str]] = ..., error: _Optional[str] = ..., successful_plan_output: _Optional[_Union[SuccessfulPlanOutput, _Mapping]] = ..., created_by: _Optional[str] = ..., created_by_principal: _Optional[_Union[_principal__client_pb2.PrincipalBasic, _Mapping]] = ...) -> None: ...

class StateUpdatePlanSummary(_message.Message):
    __slots__ = ["diff_items", "applied_by", "applied_by_principal", "created_by", "applied_at", "created_at", "workspace", "sdk_version"]
    DIFF_ITEMS_FIELD_NUMBER: _ClassVar[int]
    APPLIED_BY_FIELD_NUMBER: _ClassVar[int]
    APPLIED_BY_PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    APPLIED_AT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    SDK_VERSION_FIELD_NUMBER: _ClassVar[int]
    diff_items: _containers.RepeatedCompositeFieldContainer[StateUpdatePlanSummaryDiff]
    applied_by: str
    applied_by_principal: _principal__client_pb2.PrincipalBasic
    created_by: str
    applied_at: _timestamp_pb2.Timestamp
    created_at: _timestamp_pb2.Timestamp
    workspace: str
    sdk_version: str
    def __init__(self, diff_items: _Optional[_Iterable[_Union[StateUpdatePlanSummaryDiff, _Mapping]]] = ..., applied_by: _Optional[str] = ..., applied_by_principal: _Optional[_Union[_principal__client_pb2.PrincipalBasic, _Mapping]] = ..., created_by: _Optional[str] = ..., applied_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., workspace: _Optional[str] = ..., sdk_version: _Optional[str] = ...) -> None: ...

class StateUpdatePlanSummaryDiff(_message.Message):
    __slots__ = ["fco_type", "type", "transition_side_effects", "diffs", "name", "description", "materialization_info"]
    FCO_TYPE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSITION_SIDE_EFFECTS_FIELD_NUMBER: _ClassVar[int]
    DIFFS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_INFO_FIELD_NUMBER: _ClassVar[int]
    fco_type: str
    type: FcoTransitionType
    transition_side_effects: FcoTransitionSideEffects
    diffs: _containers.RepeatedCompositeFieldContainer[FcoPropertyDiff]
    name: str
    description: str
    materialization_info: MaterializationInfo
    def __init__(self, fco_type: _Optional[str] = ..., type: _Optional[_Union[FcoTransitionType, str]] = ..., transition_side_effects: _Optional[_Union[FcoTransitionSideEffects, _Mapping]] = ..., diffs: _Optional[_Iterable[_Union[FcoPropertyDiff, _Mapping]]] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., materialization_info: _Optional[_Union[MaterializationInfo, _Mapping]] = ...) -> None: ...
