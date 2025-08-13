from tecton_proto.spark_api import jobs__client_pb2 as _jobs__client_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaskType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNKNOWN: _ClassVar[TaskType]
    BATCH: _ClassVar[TaskType]
    STREAMING: _ClassVar[TaskType]
    INGEST: _ClassVar[TaskType]
    DELETION: _ClassVar[TaskType]
    DELTA_MAINTENANCE: _ClassVar[TaskType]
    ICEBERG_MAINTENANCE: _ClassVar[TaskType]
    FEATURE_EXPORT: _ClassVar[TaskType]
    DATASET_GENERATION: _ClassVar[TaskType]
    PLAN_INTEGRATION_TEST_BATCH: _ClassVar[TaskType]
    PLAN_INTEGRATION_TEST_STREAM: _ClassVar[TaskType]

class TaskTypeForDisplay(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNKNOWN_JOB: _ClassVar[TaskTypeForDisplay]
    BATCH_JOB: _ClassVar[TaskTypeForDisplay]
    STREAMING_JOB: _ClassVar[TaskTypeForDisplay]
    INGEST_JOB: _ClassVar[TaskTypeForDisplay]
    DELETION_JOB: _ClassVar[TaskTypeForDisplay]
    DELTA_MAINTENANCE_JOB: _ClassVar[TaskTypeForDisplay]
    FEATURE_EXPORT_JOB: _ClassVar[TaskTypeForDisplay]
    DATASET_GENERATION_JOB: _ClassVar[TaskTypeForDisplay]
    PLAN_INTEGRATION_TEST_BATCH_JOB: _ClassVar[TaskTypeForDisplay]
    PLAN_INTEGRATION_TEST_STREAM_JOB: _ClassVar[TaskTypeForDisplay]
    COMPACTION_JOB: _ClassVar[TaskTypeForDisplay]

class SparkExecutionEnvironment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    ENV_UNSPECIFIED: _ClassVar[SparkExecutionEnvironment]
    ENV_DATABRICKS_NOTEBOOK: _ClassVar[SparkExecutionEnvironment]
    ENV_EMR: _ClassVar[SparkExecutionEnvironment]
    ENV_DATAPROC: _ClassVar[SparkExecutionEnvironment]
UNKNOWN: TaskType
BATCH: TaskType
STREAMING: TaskType
INGEST: TaskType
DELETION: TaskType
DELTA_MAINTENANCE: TaskType
ICEBERG_MAINTENANCE: TaskType
FEATURE_EXPORT: TaskType
DATASET_GENERATION: TaskType
PLAN_INTEGRATION_TEST_BATCH: TaskType
PLAN_INTEGRATION_TEST_STREAM: TaskType
UNKNOWN_JOB: TaskTypeForDisplay
BATCH_JOB: TaskTypeForDisplay
STREAMING_JOB: TaskTypeForDisplay
INGEST_JOB: TaskTypeForDisplay
DELETION_JOB: TaskTypeForDisplay
DELTA_MAINTENANCE_JOB: TaskTypeForDisplay
FEATURE_EXPORT_JOB: TaskTypeForDisplay
DATASET_GENERATION_JOB: TaskTypeForDisplay
PLAN_INTEGRATION_TEST_BATCH_JOB: TaskTypeForDisplay
PLAN_INTEGRATION_TEST_STREAM_JOB: TaskTypeForDisplay
COMPACTION_JOB: TaskTypeForDisplay
ENV_UNSPECIFIED: SparkExecutionEnvironment
ENV_DATABRICKS_NOTEBOOK: SparkExecutionEnvironment
ENV_EMR: SparkExecutionEnvironment
ENV_DATAPROC: SparkExecutionEnvironment

class SparkClusterEnvironment(_message.Message):
    __slots__ = ["spark_cluster_environment_version", "job_request_templates", "merged_user_deployment_settings_version"]
    SPARK_CLUSTER_ENVIRONMENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    JOB_REQUEST_TEMPLATES_FIELD_NUMBER: _ClassVar[int]
    MERGED_USER_DEPLOYMENT_SETTINGS_VERSION_FIELD_NUMBER: _ClassVar[int]
    spark_cluster_environment_version: int
    job_request_templates: JobRequestTemplates
    merged_user_deployment_settings_version: int
    def __init__(self, spark_cluster_environment_version: _Optional[int] = ..., job_request_templates: _Optional[_Union[JobRequestTemplates, _Mapping]] = ..., merged_user_deployment_settings_version: _Optional[int] = ...) -> None: ...

class JobRequestTemplates(_message.Message):
    __slots__ = ["databricks_template", "emr_template"]
    DATABRICKS_TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    EMR_TEMPLATE_FIELD_NUMBER: _ClassVar[int]
    databricks_template: _jobs__client_pb2.StartJobRequest
    emr_template: _jobs__client_pb2.StartJobRequest
    def __init__(self, databricks_template: _Optional[_Union[_jobs__client_pb2.StartJobRequest, _Mapping]] = ..., emr_template: _Optional[_Union[_jobs__client_pb2.StartJobRequest, _Mapping]] = ...) -> None: ...
