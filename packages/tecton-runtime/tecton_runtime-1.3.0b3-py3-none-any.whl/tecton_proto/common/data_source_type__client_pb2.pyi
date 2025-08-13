from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class DataSourceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNKNOWN: _ClassVar[DataSourceType]
    BATCH: _ClassVar[DataSourceType]
    STREAM_WITH_BATCH: _ClassVar[DataSourceType]
    PUSH_NO_BATCH: _ClassVar[DataSourceType]
    PUSH_WITH_BATCH: _ClassVar[DataSourceType]
UNKNOWN: DataSourceType
BATCH: DataSourceType
STREAM_WITH_BATCH: DataSourceType
PUSH_NO_BATCH: DataSourceType
PUSH_WITH_BATCH: DataSourceType
