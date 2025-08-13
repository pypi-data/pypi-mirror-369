from google.protobuf import descriptor_pb2 as _descriptor_pb2
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Visibility(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    VISIBILITY_UNSPECIFIED: _ClassVar[Visibility]
    VISIBILITY_OMIT: _ClassVar[Visibility]
    VISIBILITY_VISIBLE: _ClassVar[Visibility]

class AuditLogTransform(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    TRANSFORM_UNSPECIFIED: _ClassVar[AuditLogTransform]
    TRANSFORM_LEGACY_ROLES: _ClassVar[AuditLogTransform]
    TRANSFORM_REDACT_STRING: _ClassVar[AuditLogTransform]
VISIBILITY_UNSPECIFIED: Visibility
VISIBILITY_OMIT: Visibility
VISIBILITY_VISIBLE: Visibility
TRANSFORM_UNSPECIFIED: AuditLogTransform
TRANSFORM_LEGACY_ROLES: AuditLogTransform
TRANSFORM_REDACT_STRING: AuditLogTransform
OPTIONS_FIELD_NUMBER: _ClassVar[int]
options: _descriptor.FieldDescriptor
AUDIT_LOG_METADATA_FIELD_NUMBER: _ClassVar[int]
audit_log_metadata: _descriptor.FieldDescriptor

class AuditLogMetadata(_message.Message):
    __slots__ = ["write_to_audit_log", "customer_facing_event_name", "version"]
    WRITE_TO_AUDIT_LOG_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FACING_EVENT_NAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    write_to_audit_log: bool
    customer_facing_event_name: str
    version: str
    def __init__(self, write_to_audit_log: bool = ..., customer_facing_event_name: _Optional[str] = ..., version: _Optional[str] = ...) -> None: ...

class AuditLogOptions(_message.Message):
    __slots__ = ["visibility", "transform"]
    VISIBILITY_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_FIELD_NUMBER: _ClassVar[int]
    visibility: Visibility
    transform: AuditLogTransform
    def __init__(self, visibility: _Optional[_Union[Visibility, str]] = ..., transform: _Optional[_Union[AuditLogTransform, str]] = ...) -> None: ...
