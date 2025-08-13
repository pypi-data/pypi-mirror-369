from tecton_proto.spark_common import clusters__client_pb2 as _clusters__client_pb2
from tecton_proto.spark_common import libraries__client_pb2 as _libraries__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NotebookTask(_message.Message):
    __slots__ = ["notebook_path", "base_parameters"]
    class BaseParametersEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NOTEBOOK_PATH_FIELD_NUMBER: _ClassVar[int]
    BASE_PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    notebook_path: str
    base_parameters: _containers.ScalarMap[str, str]
    def __init__(self, notebook_path: _Optional[str] = ..., base_parameters: _Optional[_Mapping[str, str]] = ...) -> None: ...

class RemoteLibrary(_message.Message):
    __slots__ = ["jar", "egg", "whl", "maven", "pypi"]
    JAR_FIELD_NUMBER: _ClassVar[int]
    EGG_FIELD_NUMBER: _ClassVar[int]
    WHL_FIELD_NUMBER: _ClassVar[int]
    MAVEN_FIELD_NUMBER: _ClassVar[int]
    PYPI_FIELD_NUMBER: _ClassVar[int]
    jar: str
    egg: str
    whl: str
    maven: _libraries__client_pb2.MavenLibrary
    pypi: _libraries__client_pb2.PyPiLibrary
    def __init__(self, jar: _Optional[str] = ..., egg: _Optional[str] = ..., whl: _Optional[str] = ..., maven: _Optional[_Union[_libraries__client_pb2.MavenLibrary, _Mapping]] = ..., pypi: _Optional[_Union[_libraries__client_pb2.PyPiLibrary, _Mapping]] = ...) -> None: ...

class Task(_message.Message):
    __slots__ = ["task_key", "description", "depends_on", "new_cluster", "existing_cluster_id", "notebook_task", "libraries", "timeout_seconds"]
    TASK_KEY_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    DEPENDS_ON_FIELD_NUMBER: _ClassVar[int]
    NEW_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    EXISTING_CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    NOTEBOOK_TASK_FIELD_NUMBER: _ClassVar[int]
    LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    task_key: str
    description: str
    depends_on: _containers.RepeatedCompositeFieldContainer[Task]
    new_cluster: _clusters__client_pb2.NewCluster
    existing_cluster_id: str
    notebook_task: NotebookTask
    libraries: _containers.RepeatedCompositeFieldContainer[RemoteLibrary]
    timeout_seconds: int
    def __init__(self, task_key: _Optional[str] = ..., description: _Optional[str] = ..., depends_on: _Optional[_Iterable[_Union[Task, _Mapping]]] = ..., new_cluster: _Optional[_Union[_clusters__client_pb2.NewCluster, _Mapping]] = ..., existing_cluster_id: _Optional[str] = ..., notebook_task: _Optional[_Union[NotebookTask, _Mapping]] = ..., libraries: _Optional[_Iterable[_Union[RemoteLibrary, _Mapping]]] = ..., timeout_seconds: _Optional[int] = ...) -> None: ...

class LegacyJobsRunsSubmitRequest(_message.Message):
    __slots__ = ["new_cluster", "existing_cluster_id", "notebook_task", "run_name", "libraries", "timeout_seconds", "tasks"]
    NEW_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    EXISTING_CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    NOTEBOOK_TASK_FIELD_NUMBER: _ClassVar[int]
    RUN_NAME_FIELD_NUMBER: _ClassVar[int]
    LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    new_cluster: _clusters__client_pb2.NewCluster
    existing_cluster_id: str
    notebook_task: NotebookTask
    run_name: str
    libraries: _containers.RepeatedCompositeFieldContainer[RemoteLibrary]
    timeout_seconds: int
    tasks: _containers.RepeatedCompositeFieldContainer[Task]
    def __init__(self, new_cluster: _Optional[_Union[_clusters__client_pb2.NewCluster, _Mapping]] = ..., existing_cluster_id: _Optional[str] = ..., notebook_task: _Optional[_Union[NotebookTask, _Mapping]] = ..., run_name: _Optional[str] = ..., libraries: _Optional[_Iterable[_Union[RemoteLibrary, _Mapping]]] = ..., timeout_seconds: _Optional[int] = ..., tasks: _Optional[_Iterable[_Union[Task, _Mapping]]] = ...) -> None: ...

class AccessControlList(_message.Message):
    __slots__ = ["user_name", "group_name", "service_principal_name", "permission_level"]
    class PermissionLevel(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        CAN_MANAGE: _ClassVar[AccessControlList.PermissionLevel]
        IS_OWNER: _ClassVar[AccessControlList.PermissionLevel]
        CAN_MANAGE_RUN: _ClassVar[AccessControlList.PermissionLevel]
        CAN_VIEW: _ClassVar[AccessControlList.PermissionLevel]
    CAN_MANAGE: AccessControlList.PermissionLevel
    IS_OWNER: AccessControlList.PermissionLevel
    CAN_MANAGE_RUN: AccessControlList.PermissionLevel
    CAN_VIEW: AccessControlList.PermissionLevel
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    SERVICE_PRINCIPAL_NAME_FIELD_NUMBER: _ClassVar[int]
    PERMISSION_LEVEL_FIELD_NUMBER: _ClassVar[int]
    user_name: str
    group_name: str
    service_principal_name: str
    permission_level: AccessControlList.PermissionLevel
    def __init__(self, user_name: _Optional[str] = ..., group_name: _Optional[str] = ..., service_principal_name: _Optional[str] = ..., permission_level: _Optional[_Union[AccessControlList.PermissionLevel, str]] = ...) -> None: ...

class RunAs(_message.Message):
    __slots__ = ["user_name", "service_principal_name"]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    SERVICE_PRINCIPAL_NAME_FIELD_NUMBER: _ClassVar[int]
    user_name: str
    service_principal_name: str
    def __init__(self, user_name: _Optional[str] = ..., service_principal_name: _Optional[str] = ...) -> None: ...

class JobsRunsSubmitRequest(_message.Message):
    __slots__ = ["run_name", "timeout_seconds", "idempotency_token", "tasks", "access_control_list", "run_as"]
    RUN_NAME_FIELD_NUMBER: _ClassVar[int]
    TIMEOUT_SECONDS_FIELD_NUMBER: _ClassVar[int]
    IDEMPOTENCY_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TASKS_FIELD_NUMBER: _ClassVar[int]
    ACCESS_CONTROL_LIST_FIELD_NUMBER: _ClassVar[int]
    RUN_AS_FIELD_NUMBER: _ClassVar[int]
    run_name: str
    timeout_seconds: int
    idempotency_token: str
    tasks: _containers.RepeatedCompositeFieldContainer[Task]
    access_control_list: _containers.RepeatedCompositeFieldContainer[AccessControlList]
    run_as: RunAs
    def __init__(self, run_name: _Optional[str] = ..., timeout_seconds: _Optional[int] = ..., idempotency_token: _Optional[str] = ..., tasks: _Optional[_Iterable[_Union[Task, _Mapping]]] = ..., access_control_list: _Optional[_Iterable[_Union[AccessControlList, _Mapping]]] = ..., run_as: _Optional[_Union[RunAs, _Mapping]] = ...) -> None: ...

class JobsRunsSubmitResponse(_message.Message):
    __slots__ = ["run_id"]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    run_id: int
    def __init__(self, run_id: _Optional[int] = ...) -> None: ...

class JobsRunsGetRequest(_message.Message):
    __slots__ = ["run_id"]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    run_id: int
    def __init__(self, run_id: _Optional[int] = ...) -> None: ...

class JobsRunsGetResponse(_message.Message):
    __slots__ = ["run_id", "job_id", "execution_duration", "start_time", "end_time", "setup_duration", "cluster_instance", "run_page_url", "state"]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    EXECUTION_DURATION_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    SETUP_DURATION_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_INSTANCE_FIELD_NUMBER: _ClassVar[int]
    RUN_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    run_id: int
    job_id: int
    execution_duration: int
    start_time: int
    end_time: int
    setup_duration: int
    cluster_instance: ClusterInstance
    run_page_url: str
    state: RunState
    def __init__(self, run_id: _Optional[int] = ..., job_id: _Optional[int] = ..., execution_duration: _Optional[int] = ..., start_time: _Optional[int] = ..., end_time: _Optional[int] = ..., setup_duration: _Optional[int] = ..., cluster_instance: _Optional[_Union[ClusterInstance, _Mapping]] = ..., run_page_url: _Optional[str] = ..., state: _Optional[_Union[RunState, _Mapping]] = ...) -> None: ...

class ClusterInstance(_message.Message):
    __slots__ = ["cluster_id"]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    cluster_id: str
    def __init__(self, cluster_id: _Optional[str] = ...) -> None: ...

class RunState(_message.Message):
    __slots__ = ["life_cycle_state", "result_state", "state_message"]
    class RunLifeCycleState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        UNKNOWN_RUN_LIFE_CYCLE_STATE: _ClassVar[RunState.RunLifeCycleState]
        PENDING: _ClassVar[RunState.RunLifeCycleState]
        RUNNING: _ClassVar[RunState.RunLifeCycleState]
        TERMINATING: _ClassVar[RunState.RunLifeCycleState]
        TERMINATED: _ClassVar[RunState.RunLifeCycleState]
        SKIPPED: _ClassVar[RunState.RunLifeCycleState]
        INTERNAL_ERROR: _ClassVar[RunState.RunLifeCycleState]
    UNKNOWN_RUN_LIFE_CYCLE_STATE: RunState.RunLifeCycleState
    PENDING: RunState.RunLifeCycleState
    RUNNING: RunState.RunLifeCycleState
    TERMINATING: RunState.RunLifeCycleState
    TERMINATED: RunState.RunLifeCycleState
    SKIPPED: RunState.RunLifeCycleState
    INTERNAL_ERROR: RunState.RunLifeCycleState
    class RunResultState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        UNKNOWN_RUN_RESULT_STATE: _ClassVar[RunState.RunResultState]
        SUCCESS: _ClassVar[RunState.RunResultState]
        FAILED: _ClassVar[RunState.RunResultState]
        TIMEDOUT: _ClassVar[RunState.RunResultState]
        CANCELED: _ClassVar[RunState.RunResultState]
    UNKNOWN_RUN_RESULT_STATE: RunState.RunResultState
    SUCCESS: RunState.RunResultState
    FAILED: RunState.RunResultState
    TIMEDOUT: RunState.RunResultState
    CANCELED: RunState.RunResultState
    LIFE_CYCLE_STATE_FIELD_NUMBER: _ClassVar[int]
    RESULT_STATE_FIELD_NUMBER: _ClassVar[int]
    STATE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    life_cycle_state: RunState.RunLifeCycleState
    result_state: RunState.RunResultState
    state_message: str
    def __init__(self, life_cycle_state: _Optional[_Union[RunState.RunLifeCycleState, str]] = ..., result_state: _Optional[_Union[RunState.RunResultState, str]] = ..., state_message: _Optional[str] = ...) -> None: ...

class JobsCancelRunRequest(_message.Message):
    __slots__ = ["run_id"]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    run_id: int
    def __init__(self, run_id: _Optional[int] = ...) -> None: ...

class JobsRunsListRequest(_message.Message):
    __slots__ = ["offset", "active_only", "run_type", "limit"]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_ONLY_FIELD_NUMBER: _ClassVar[int]
    RUN_TYPE_FIELD_NUMBER: _ClassVar[int]
    LIMIT_FIELD_NUMBER: _ClassVar[int]
    offset: int
    active_only: bool
    run_type: str
    limit: int
    def __init__(self, offset: _Optional[int] = ..., active_only: bool = ..., run_type: _Optional[str] = ..., limit: _Optional[int] = ...) -> None: ...

class NewCluster(_message.Message):
    __slots__ = ["custom_tags"]
    class CustomTagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    CUSTOM_TAGS_FIELD_NUMBER: _ClassVar[int]
    custom_tags: _containers.ScalarMap[str, str]
    def __init__(self, custom_tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class ClusterSpec(_message.Message):
    __slots__ = ["new_cluster", "existing_cluster_id", "libraries"]
    NEW_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    EXISTING_CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    LIBRARIES_FIELD_NUMBER: _ClassVar[int]
    new_cluster: NewCluster
    existing_cluster_id: str
    libraries: _containers.RepeatedCompositeFieldContainer[RemoteLibrary]
    def __init__(self, new_cluster: _Optional[_Union[NewCluster, _Mapping]] = ..., existing_cluster_id: _Optional[str] = ..., libraries: _Optional[_Iterable[_Union[RemoteLibrary, _Mapping]]] = ...) -> None: ...

class Run(_message.Message):
    __slots__ = ["job_id", "run_id", "state", "cluster_spec", "run_page_url"]
    JOB_ID_FIELD_NUMBER: _ClassVar[int]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_SPEC_FIELD_NUMBER: _ClassVar[int]
    RUN_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    job_id: int
    run_id: int
    state: RunState
    cluster_spec: ClusterSpec
    run_page_url: str
    def __init__(self, job_id: _Optional[int] = ..., run_id: _Optional[int] = ..., state: _Optional[_Union[RunState, _Mapping]] = ..., cluster_spec: _Optional[_Union[ClusterSpec, _Mapping]] = ..., run_page_url: _Optional[str] = ...) -> None: ...

class JobsRunsListResponse(_message.Message):
    __slots__ = ["runs", "has_more"]
    RUNS_FIELD_NUMBER: _ClassVar[int]
    HAS_MORE_FIELD_NUMBER: _ClassVar[int]
    runs: _containers.RepeatedCompositeFieldContainer[Run]
    has_more: bool
    def __init__(self, runs: _Optional[_Iterable[_Union[Run, _Mapping]]] = ..., has_more: bool = ...) -> None: ...
