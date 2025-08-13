from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class ColumnType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    COLUMN_TYPE_UNKNOWN: _ClassVar[ColumnType]
    COLUMN_TYPE_INT64: _ClassVar[ColumnType]
    COLUMN_TYPE_DOUBLE: _ClassVar[ColumnType]
    COLUMN_TYPE_STRING: _ClassVar[ColumnType]
    COLUMN_TYPE_BOOL: _ClassVar[ColumnType]
    COLUMN_TYPE_STRING_ARRAY: _ClassVar[ColumnType]
    COLUMN_TYPE_INT64_ARRAY: _ClassVar[ColumnType]
    COLUMN_TYPE_DOUBLE_ARRAY: _ClassVar[ColumnType]
    COLUMN_TYPE_FLOAT_ARRAY: _ClassVar[ColumnType]
    COLUMN_TYPE_DERIVE_FROM_DATA_TYPE: _ClassVar[ColumnType]
COLUMN_TYPE_UNKNOWN: ColumnType
COLUMN_TYPE_INT64: ColumnType
COLUMN_TYPE_DOUBLE: ColumnType
COLUMN_TYPE_STRING: ColumnType
COLUMN_TYPE_BOOL: ColumnType
COLUMN_TYPE_STRING_ARRAY: ColumnType
COLUMN_TYPE_INT64_ARRAY: ColumnType
COLUMN_TYPE_DOUBLE_ARRAY: ColumnType
COLUMN_TYPE_FLOAT_ARRAY: ColumnType
COLUMN_TYPE_DERIVE_FROM_DATA_TYPE: ColumnType
