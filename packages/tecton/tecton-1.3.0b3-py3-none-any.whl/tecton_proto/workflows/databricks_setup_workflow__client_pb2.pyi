from tecton_proto.data import user_deployment_settings__client_pb2 as _user_deployment_settings__client_pb2
from tecton_proto.workflows import state_machine_workflow__client_pb2 as _state_machine_workflow__client_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DatabricksSetupWorkflowState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    DATABRICKS_SETUP_WORKFLOW_UNKNOWN: _ClassVar[DatabricksSetupWorkflowState]
    DATABRICKS_SETUP_WORKFLOW_WAITING_FOR_SETTINGS: _ClassVar[DatabricksSetupWorkflowState]
    DATABRICKS_SETUP_WORKFLOW_FOUND_SETTINGS: _ClassVar[DatabricksSetupWorkflowState]
    DATABRICKS_SETUP_WORKFLOW_CREATED_SECRET_SCOPE: _ClassVar[DatabricksSetupWorkflowState]
    DATABRICKS_SETUP_WORKFLOW_CLUSTER_STARTING: _ClassVar[DatabricksSetupWorkflowState]
    DATABRICKS_SETUP_WORKFLOW_CLUSTER_READY: _ClassVar[DatabricksSetupWorkflowState]
DATABRICKS_SETUP_WORKFLOW_UNKNOWN: DatabricksSetupWorkflowState
DATABRICKS_SETUP_WORKFLOW_WAITING_FOR_SETTINGS: DatabricksSetupWorkflowState
DATABRICKS_SETUP_WORKFLOW_FOUND_SETTINGS: DatabricksSetupWorkflowState
DATABRICKS_SETUP_WORKFLOW_CREATED_SECRET_SCOPE: DatabricksSetupWorkflowState
DATABRICKS_SETUP_WORKFLOW_CLUSTER_STARTING: DatabricksSetupWorkflowState
DATABRICKS_SETUP_WORKFLOW_CLUSTER_READY: DatabricksSetupWorkflowState

class DatabricksSetupWorkflow(_message.Message):
    __slots__ = ["state", "user_deployment_settings", "failed_advances_for_version", "created_secret_scope", "notebook_cluster_id", "error_message"]
    STATE_FIELD_NUMBER: _ClassVar[int]
    USER_DEPLOYMENT_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    FAILED_ADVANCES_FOR_VERSION_FIELD_NUMBER: _ClassVar[int]
    CREATED_SECRET_SCOPE_FIELD_NUMBER: _ClassVar[int]
    NOTEBOOK_CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    state: DatabricksSetupWorkflowState
    user_deployment_settings: _user_deployment_settings__client_pb2.UserDeploymentSettings
    failed_advances_for_version: int
    created_secret_scope: bool
    notebook_cluster_id: str
    error_message: str
    def __init__(self, state: _Optional[_Union[DatabricksSetupWorkflowState, str]] = ..., user_deployment_settings: _Optional[_Union[_user_deployment_settings__client_pb2.UserDeploymentSettings, _Mapping]] = ..., failed_advances_for_version: _Optional[int] = ..., created_secret_scope: bool = ..., notebook_cluster_id: _Optional[str] = ..., error_message: _Optional[str] = ...) -> None: ...
