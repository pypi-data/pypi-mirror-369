from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import framework_version__client_pb2 as _framework_version__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class FcoMetadata(_message.Message):
    __slots__ = ["name", "description", "created_at", "owner", "last_modified_by", "is_archived", "workspace", "workspace_state_id", "family", "scope", "source_lineno", "source_filename", "tags", "framework_version", "last_updated_at"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    OWNER_FIELD_NUMBER: _ClassVar[int]
    LAST_MODIFIED_BY_FIELD_NUMBER: _ClassVar[int]
    IS_ARCHIVED_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_STATE_ID_FIELD_NUMBER: _ClassVar[int]
    FAMILY_FIELD_NUMBER: _ClassVar[int]
    SCOPE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_LINENO_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FILENAME_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    FRAMEWORK_VERSION_FIELD_NUMBER: _ClassVar[int]
    LAST_UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    created_at: _timestamp_pb2.Timestamp
    owner: str
    last_modified_by: str
    is_archived: bool
    workspace: str
    workspace_state_id: _id__client_pb2.Id
    family: str
    scope: str
    source_lineno: str
    source_filename: str
    tags: _containers.ScalarMap[str, str]
    framework_version: _framework_version__client_pb2.FrameworkVersion
    last_updated_at: _timestamp_pb2.Timestamp
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., owner: _Optional[str] = ..., last_modified_by: _Optional[str] = ..., is_archived: bool = ..., workspace: _Optional[str] = ..., workspace_state_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., family: _Optional[str] = ..., scope: _Optional[str] = ..., source_lineno: _Optional[str] = ..., source_filename: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ..., framework_version: _Optional[_Union[_framework_version__client_pb2.FrameworkVersion, str]] = ..., last_updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...
