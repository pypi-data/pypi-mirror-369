from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class ServerGroupType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    SERVER_GROUP_TYPE_UNSPECIFIED: _ClassVar[ServerGroupType]
    SERVER_GROUP_TYPE_FEATURE_SERVER_GROUP: _ClassVar[ServerGroupType]
    SERVER_GROUP_TYPE_TRANSFORM_SERVER_GROUP: _ClassVar[ServerGroupType]
    SERVER_GROUP_TYPE_INGEST_SERVER_GROUP: _ClassVar[ServerGroupType]
SERVER_GROUP_TYPE_UNSPECIFIED: ServerGroupType
SERVER_GROUP_TYPE_FEATURE_SERVER_GROUP: ServerGroupType
SERVER_GROUP_TYPE_TRANSFORM_SERVER_GROUP: ServerGroupType
SERVER_GROUP_TYPE_INGEST_SERVER_GROUP: ServerGroupType
