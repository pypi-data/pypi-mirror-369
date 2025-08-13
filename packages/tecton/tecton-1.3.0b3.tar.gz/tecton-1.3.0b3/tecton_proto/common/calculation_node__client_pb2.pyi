from tecton_proto.common import data_type__client_pb2 as _data_type__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OperationType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    OPERATION_UNSPECIFIED: _ClassVar[OperationType]
    ADDITION: _ClassVar[OperationType]
    SUBTRACTION: _ClassVar[OperationType]
    MULTIPLICATION: _ClassVar[OperationType]
    DIVISION: _ClassVar[OperationType]
    COALESCE: _ClassVar[OperationType]
    DATE_DIFF: _ClassVar[OperationType]
    EQUALS: _ClassVar[OperationType]
    NOT_EQUALS: _ClassVar[OperationType]
    LESS_THAN: _ClassVar[OperationType]
    LESS_THAN_EQUALS: _ClassVar[OperationType]
    GREATER_THAN: _ClassVar[OperationType]
    GREATER_THAN_EQUALS: _ClassVar[OperationType]
    AND: _ClassVar[OperationType]
    OR: _ClassVar[OperationType]
    NOT: _ClassVar[OperationType]
    TRY_STRPTIME: _ClassVar[OperationType]

class DatePart(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    DATE_PART_UNSPECIFIED: _ClassVar[DatePart]
    DAY: _ClassVar[DatePart]
    MONTH: _ClassVar[DatePart]
    WEEK: _ClassVar[DatePart]
    YEAR: _ClassVar[DatePart]
    SECOND: _ClassVar[DatePart]
    HOUR: _ClassVar[DatePart]
    MINUTE: _ClassVar[DatePart]
    MILLENNIUM: _ClassVar[DatePart]
    CENTURY: _ClassVar[DatePart]
    DECADE: _ClassVar[DatePart]
    QUARTER: _ClassVar[DatePart]
    MILLISECONDS: _ClassVar[DatePart]
    MICROSECONDS: _ClassVar[DatePart]
OPERATION_UNSPECIFIED: OperationType
ADDITION: OperationType
SUBTRACTION: OperationType
MULTIPLICATION: OperationType
DIVISION: OperationType
COALESCE: OperationType
DATE_DIFF: OperationType
EQUALS: OperationType
NOT_EQUALS: OperationType
LESS_THAN: OperationType
LESS_THAN_EQUALS: OperationType
GREATER_THAN: OperationType
GREATER_THAN_EQUALS: OperationType
AND: OperationType
OR: OperationType
NOT: OperationType
TRY_STRPTIME: OperationType
DATE_PART_UNSPECIFIED: DatePart
DAY: DatePart
MONTH: DatePart
WEEK: DatePart
YEAR: DatePart
SECOND: DatePart
HOUR: DatePart
MINUTE: DatePart
MILLENNIUM: DatePart
CENTURY: DatePart
DECADE: DatePart
QUARTER: DatePart
MILLISECONDS: DatePart
MICROSECONDS: DatePart

class NullLiteralValue(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class LiteralValue(_message.Message):
    __slots__ = ["float32_value", "float64_value", "int64_value", "bool_value", "string_value", "null_value"]
    FLOAT32_VALUE_FIELD_NUMBER: _ClassVar[int]
    FLOAT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    INT64_VALUE_FIELD_NUMBER: _ClassVar[int]
    BOOL_VALUE_FIELD_NUMBER: _ClassVar[int]
    STRING_VALUE_FIELD_NUMBER: _ClassVar[int]
    NULL_VALUE_FIELD_NUMBER: _ClassVar[int]
    float32_value: float
    float64_value: float
    int64_value: int
    bool_value: bool
    string_value: str
    null_value: NullLiteralValue
    def __init__(self, float32_value: _Optional[float] = ..., float64_value: _Optional[float] = ..., int64_value: _Optional[int] = ..., bool_value: bool = ..., string_value: _Optional[str] = ..., null_value: _Optional[_Union[NullLiteralValue, _Mapping]] = ...) -> None: ...

class Operation(_message.Message):
    __slots__ = ["operation", "operands"]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    OPERANDS_FIELD_NUMBER: _ClassVar[int]
    operation: OperationType
    operands: _containers.RepeatedCompositeFieldContainer[AbstractSyntaxTreeNode]
    def __init__(self, operation: _Optional[_Union[OperationType, str]] = ..., operands: _Optional[_Iterable[_Union[AbstractSyntaxTreeNode, _Mapping]]] = ...) -> None: ...

class WhenClause(_message.Message):
    __slots__ = ["condition", "result"]
    CONDITION_FIELD_NUMBER: _ClassVar[int]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    condition: AbstractSyntaxTreeNode
    result: AbstractSyntaxTreeNode
    def __init__(self, condition: _Optional[_Union[AbstractSyntaxTreeNode, _Mapping]] = ..., result: _Optional[_Union[AbstractSyntaxTreeNode, _Mapping]] = ...) -> None: ...

class ElseClause(_message.Message):
    __slots__ = ["result"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    result: AbstractSyntaxTreeNode
    def __init__(self, result: _Optional[_Union[AbstractSyntaxTreeNode, _Mapping]] = ...) -> None: ...

class CaseStatement(_message.Message):
    __slots__ = ["when_clauses", "else_clause"]
    WHEN_CLAUSES_FIELD_NUMBER: _ClassVar[int]
    ELSE_CLAUSE_FIELD_NUMBER: _ClassVar[int]
    when_clauses: _containers.RepeatedCompositeFieldContainer[WhenClause]
    else_clause: ElseClause
    def __init__(self, when_clauses: _Optional[_Iterable[_Union[WhenClause, _Mapping]]] = ..., else_clause: _Optional[_Union[ElseClause, _Mapping]] = ...) -> None: ...

class AbstractSyntaxTreeNode(_message.Message):
    __slots__ = ["dtype", "literal_value", "column_reference", "operation", "date_part", "case_statement"]
    DTYPE_FIELD_NUMBER: _ClassVar[int]
    LITERAL_VALUE_FIELD_NUMBER: _ClassVar[int]
    COLUMN_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    OPERATION_FIELD_NUMBER: _ClassVar[int]
    DATE_PART_FIELD_NUMBER: _ClassVar[int]
    CASE_STATEMENT_FIELD_NUMBER: _ClassVar[int]
    dtype: _data_type__client_pb2.DataType
    literal_value: LiteralValue
    column_reference: str
    operation: Operation
    date_part: DatePart
    case_statement: CaseStatement
    def __init__(self, dtype: _Optional[_Union[_data_type__client_pb2.DataType, _Mapping]] = ..., literal_value: _Optional[_Union[LiteralValue, _Mapping]] = ..., column_reference: _Optional[str] = ..., operation: _Optional[_Union[Operation, _Mapping]] = ..., date_part: _Optional[_Union[DatePart, str]] = ..., case_statement: _Optional[_Union[CaseStatement, _Mapping]] = ...) -> None: ...
