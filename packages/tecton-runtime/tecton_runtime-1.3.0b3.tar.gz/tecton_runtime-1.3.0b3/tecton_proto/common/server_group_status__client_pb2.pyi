from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class ServerGroupStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    SERVER_GROUP_STATUS_UNSPECIFIED: _ClassVar[ServerGroupStatus]
    SERVER_GROUP_STATUS_CREATING: _ClassVar[ServerGroupStatus]
    SERVER_GROUP_STATUS_PENDING: _ClassVar[ServerGroupStatus]
    SERVER_GROUP_STATUS_READY: _ClassVar[ServerGroupStatus]
    SERVER_GROUP_STATUS_UPDATING: _ClassVar[ServerGroupStatus]
    SERVER_GROUP_STATUS_ERROR: _ClassVar[ServerGroupStatus]
    SERVER_GROUP_STATUS_DELETING: _ClassVar[ServerGroupStatus]
SERVER_GROUP_STATUS_UNSPECIFIED: ServerGroupStatus
SERVER_GROUP_STATUS_CREATING: ServerGroupStatus
SERVER_GROUP_STATUS_PENDING: ServerGroupStatus
SERVER_GROUP_STATUS_READY: ServerGroupStatus
SERVER_GROUP_STATUS_UPDATING: ServerGroupStatus
SERVER_GROUP_STATUS_ERROR: ServerGroupStatus
SERVER_GROUP_STATUS_DELETING: ServerGroupStatus
