from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class Secret(_message.Message):
    __slots__ = ["value", "redacted_value", "encrypted_value"]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    REDACTED_VALUE_FIELD_NUMBER: _ClassVar[int]
    ENCRYPTED_VALUE_FIELD_NUMBER: _ClassVar[int]
    value: str
    redacted_value: str
    encrypted_value: str
    def __init__(self, value: _Optional[str] = ..., redacted_value: _Optional[str] = ..., encrypted_value: _Optional[str] = ...) -> None: ...

class SecretReference(_message.Message):
    __slots__ = ["scope", "key", "is_local"]
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    IS_LOCAL_FIELD_NUMBER: _ClassVar[int]
    scope: str
    key: str
    is_local: bool
    def __init__(self, scope: _Optional[str] = ..., key: _Optional[str] = ..., is_local: bool = ...) -> None: ...
