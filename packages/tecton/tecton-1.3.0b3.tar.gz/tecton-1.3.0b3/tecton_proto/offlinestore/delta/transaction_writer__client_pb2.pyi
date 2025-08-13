from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import aws_credentials__client_pb2 as _aws_credentials__client_pb2
from tecton_proto.common import schema__client_pb2 as _schema__client_pb2
from tecton_proto.offlinestore.delta import metadata__client_pb2 as _metadata__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InitializeArgs(_message.Message):
    __slots__ = ["path", "id", "name", "description", "schema", "partition_columns", "dynamodb_log_table_name", "dynamodb_log_table_region", "cross_account_role_configs", "kms_key_arn"]
    PATH_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    PARTITION_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    DYNAMODB_LOG_TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    DYNAMODB_LOG_TABLE_REGION_FIELD_NUMBER: _ClassVar[int]
    CROSS_ACCOUNT_ROLE_CONFIGS_FIELD_NUMBER: _ClassVar[int]
    KMS_KEY_ARN_FIELD_NUMBER: _ClassVar[int]
    path: str
    id: str
    name: str
    description: str
    schema: _schema__client_pb2.Schema
    partition_columns: _containers.RepeatedScalarFieldContainer[str]
    dynamodb_log_table_name: str
    dynamodb_log_table_region: str
    cross_account_role_configs: CrossAccountRoleConfig
    kms_key_arn: str
    def __init__(self, path: _Optional[str] = ..., id: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., schema: _Optional[_Union[_schema__client_pb2.Schema, _Mapping]] = ..., partition_columns: _Optional[_Iterable[str]] = ..., dynamodb_log_table_name: _Optional[str] = ..., dynamodb_log_table_region: _Optional[str] = ..., cross_account_role_configs: _Optional[_Union[CrossAccountRoleConfig, _Mapping]] = ..., kms_key_arn: _Optional[str] = ...) -> None: ...

class AddFile(_message.Message):
    __slots__ = ["uri", "partition_values", "tags", "stats"]
    class PartitionValuesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    URI_FIELD_NUMBER: _ClassVar[int]
    PARTITION_VALUES_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    STATS_FIELD_NUMBER: _ClassVar[int]
    uri: str
    partition_values: _containers.ScalarMap[str, str]
    tags: _containers.ScalarMap[str, str]
    stats: str
    def __init__(self, uri: _Optional[str] = ..., partition_values: _Optional[_Mapping[str, str]] = ..., tags: _Optional[_Mapping[str, str]] = ..., stats: _Optional[str] = ...) -> None: ...

class UpdateArgs(_message.Message):
    __slots__ = ["add_files", "user_metadata", "delete_uris"]
    ADD_FILES_FIELD_NUMBER: _ClassVar[int]
    USER_METADATA_FIELD_NUMBER: _ClassVar[int]
    DELETE_URIS_FIELD_NUMBER: _ClassVar[int]
    add_files: _containers.RepeatedCompositeFieldContainer[AddFile]
    user_metadata: _metadata__client_pb2.TectonDeltaMetadata
    delete_uris: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, add_files: _Optional[_Iterable[_Union[AddFile, _Mapping]]] = ..., user_metadata: _Optional[_Union[_metadata__client_pb2.TectonDeltaMetadata, _Mapping]] = ..., delete_uris: _Optional[_Iterable[str]] = ...) -> None: ...

class UpdateResult(_message.Message):
    __slots__ = ["committed_version", "error_type", "error_message"]
    class ErrorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        ERROR_UNSPECIFIED: _ClassVar[UpdateResult.ErrorType]
        ERROR_UNKNOWN: _ClassVar[UpdateResult.ErrorType]
        CONCURRENT_APPEND_ERROR: _ClassVar[UpdateResult.ErrorType]
        CONCURRENT_DELETE_READ_ERROR: _ClassVar[UpdateResult.ErrorType]
        CONCURRENT_DELETE_DELETE_ERROR: _ClassVar[UpdateResult.ErrorType]
        METADATA_CHANGED_ERROR: _ClassVar[UpdateResult.ErrorType]
        CONCURRENT_TRANSACTION_ERROR: _ClassVar[UpdateResult.ErrorType]
        PROTOCOL_CHANGED_ERROR: _ClassVar[UpdateResult.ErrorType]
    ERROR_UNSPECIFIED: UpdateResult.ErrorType
    ERROR_UNKNOWN: UpdateResult.ErrorType
    CONCURRENT_APPEND_ERROR: UpdateResult.ErrorType
    CONCURRENT_DELETE_READ_ERROR: UpdateResult.ErrorType
    CONCURRENT_DELETE_DELETE_ERROR: UpdateResult.ErrorType
    METADATA_CHANGED_ERROR: UpdateResult.ErrorType
    CONCURRENT_TRANSACTION_ERROR: UpdateResult.ErrorType
    PROTOCOL_CHANGED_ERROR: UpdateResult.ErrorType
    COMMITTED_VERSION_FIELD_NUMBER: _ClassVar[int]
    ERROR_TYPE_FIELD_NUMBER: _ClassVar[int]
    ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    committed_version: int
    error_type: UpdateResult.ErrorType
    error_message: str
    def __init__(self, committed_version: _Optional[int] = ..., error_type: _Optional[_Union[UpdateResult.ErrorType, str]] = ..., error_message: _Optional[str] = ...) -> None: ...

class Expression(_message.Message):
    __slots__ = ["column", "literal", "binary"]
    class Literal(_message.Message):
        __slots__ = ["str", "timestamp", "int64", "bool"]
        STR_FIELD_NUMBER: _ClassVar[int]
        TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
        INT64_FIELD_NUMBER: _ClassVar[int]
        BOOL_FIELD_NUMBER: _ClassVar[int]
        str: str
        timestamp: _timestamp_pb2.Timestamp
        int64: int
        bool: bool
        def __init__(self, str: _Optional[str] = ..., timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., int64: _Optional[int] = ..., bool: bool = ...) -> None: ...
    class Binary(_message.Message):
        __slots__ = ["op", "left", "right"]
        class Op(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = []
            OP_UNSPECIFIED: _ClassVar[Expression.Binary.Op]
            OP_AND: _ClassVar[Expression.Binary.Op]
            OP_LT: _ClassVar[Expression.Binary.Op]
            OP_LE: _ClassVar[Expression.Binary.Op]
            OP_EQ: _ClassVar[Expression.Binary.Op]
            OP_OR: _ClassVar[Expression.Binary.Op]
        OP_UNSPECIFIED: Expression.Binary.Op
        OP_AND: Expression.Binary.Op
        OP_LT: Expression.Binary.Op
        OP_LE: Expression.Binary.Op
        OP_EQ: Expression.Binary.Op
        OP_OR: Expression.Binary.Op
        OP_FIELD_NUMBER: _ClassVar[int]
        LEFT_FIELD_NUMBER: _ClassVar[int]
        RIGHT_FIELD_NUMBER: _ClassVar[int]
        op: Expression.Binary.Op
        left: Expression
        right: Expression
        def __init__(self, op: _Optional[_Union[Expression.Binary.Op, str]] = ..., left: _Optional[_Union[Expression, _Mapping]] = ..., right: _Optional[_Union[Expression, _Mapping]] = ...) -> None: ...
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    LITERAL_FIELD_NUMBER: _ClassVar[int]
    BINARY_FIELD_NUMBER: _ClassVar[int]
    column: _schema__client_pb2.Column
    literal: Expression.Literal
    binary: Expression.Binary
    def __init__(self, column: _Optional[_Union[_schema__client_pb2.Column, _Mapping]] = ..., literal: _Optional[_Union[Expression.Literal, _Mapping]] = ..., binary: _Optional[_Union[Expression.Binary, _Mapping]] = ...) -> None: ...

class ReadForUpdateArgs(_message.Message):
    __slots__ = ["read_predicate"]
    READ_PREDICATE_FIELD_NUMBER: _ClassVar[int]
    read_predicate: Expression
    def __init__(self, read_predicate: _Optional[_Union[Expression, _Mapping]] = ...) -> None: ...

class ReadForUpdateResult(_message.Message):
    __slots__ = ["uris"]
    URIS_FIELD_NUMBER: _ClassVar[int]
    uris: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, uris: _Optional[_Iterable[str]] = ...) -> None: ...

class GetPartitionsArgs(_message.Message):
    __slots__ = ["tags"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    TAGS_FIELD_NUMBER: _ClassVar[int]
    tags: _containers.ScalarMap[str, str]
    def __init__(self, tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class GetPartitionsResult(_message.Message):
    __slots__ = ["partitions"]
    class Partition(_message.Message):
        __slots__ = ["values"]
        class ValuesEntry(_message.Message):
            __slots__ = ["key", "value"]
            KEY_FIELD_NUMBER: _ClassVar[int]
            VALUE_FIELD_NUMBER: _ClassVar[int]
            key: str
            value: str
            def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
        VALUES_FIELD_NUMBER: _ClassVar[int]
        values: _containers.ScalarMap[str, str]
        def __init__(self, values: _Optional[_Mapping[str, str]] = ...) -> None: ...
    PARTITIONS_FIELD_NUMBER: _ClassVar[int]
    partitions: _containers.RepeatedCompositeFieldContainer[GetPartitionsResult.Partition]
    def __init__(self, partitions: _Optional[_Iterable[_Union[GetPartitionsResult.Partition, _Mapping]]] = ...) -> None: ...

class CrossAccountRoleConfig(_message.Message):
    __slots__ = ["s3_cross_account_role", "dynamo_cross_account_role"]
    S3_CROSS_ACCOUNT_ROLE_FIELD_NUMBER: _ClassVar[int]
    DYNAMO_CROSS_ACCOUNT_ROLE_FIELD_NUMBER: _ClassVar[int]
    s3_cross_account_role: _aws_credentials__client_pb2.AwsIamRole
    dynamo_cross_account_role: _aws_credentials__client_pb2.AwsIamRole
    def __init__(self, s3_cross_account_role: _Optional[_Union[_aws_credentials__client_pb2.AwsIamRole, _Mapping]] = ..., dynamo_cross_account_role: _Optional[_Union[_aws_credentials__client_pb2.AwsIamRole, _Mapping]] = ...) -> None: ...
