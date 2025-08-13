from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.auth import principal__client_pb2 as _principal__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import schema__client_pb2 as _schema__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ModelArtifactStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    STATUS_UNSPECIFIED: _ClassVar[ModelArtifactStatus]
    PENDING_FILE: _ClassVar[ModelArtifactStatus]
    PENDING_SCAN: _ClassVar[ModelArtifactStatus]
    READY: _ClassVar[ModelArtifactStatus]
    ERROR: _ClassVar[ModelArtifactStatus]
    DELETED: _ClassVar[ModelArtifactStatus]

class ModelType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    MODEL_TYPE_UNSPECIFIED: _ClassVar[ModelType]
    TECTON_TEXT_EMBEDDING: _ClassVar[ModelType]
    PYTORCH: _ClassVar[ModelType]
    PYTHON: _ClassVar[ModelType]
STATUS_UNSPECIFIED: ModelArtifactStatus
PENDING_FILE: ModelArtifactStatus
PENDING_SCAN: ModelArtifactStatus
READY: ModelArtifactStatus
ERROR: ModelArtifactStatus
DELETED: ModelArtifactStatus
MODEL_TYPE_UNSPECIFIED: ModelType
TECTON_TEXT_EMBEDDING: ModelType
PYTORCH: ModelType
PYTHON: ModelType

class ModelArtifactInfo(_message.Message):
    __slots__ = ["id", "name", "type", "description", "file_hashes", "input_schema", "output_schema", "tags", "storage_path", "status", "created_at", "updated_at", "model_file_path", "model_config_file_path", "artifact_files", "environments", "created_by", "created_by_principal"]
    class FileHashesEntry(_message.Message):
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
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    FILE_HASHES_FIELD_NUMBER: _ClassVar[int]
    INPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    STORAGE_PATH_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    UPDATED_AT_FIELD_NUMBER: _ClassVar[int]
    MODEL_FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    MODEL_CONFIG_FILE_PATH_FIELD_NUMBER: _ClassVar[int]
    ARTIFACT_FILES_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENTS_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_FIELD_NUMBER: _ClassVar[int]
    CREATED_BY_PRINCIPAL_FIELD_NUMBER: _ClassVar[int]
    id: _id__client_pb2.Id
    name: str
    type: ModelType
    description: str
    file_hashes: _containers.ScalarMap[str, str]
    input_schema: _schema__client_pb2.Schema
    output_schema: _schema__client_pb2.Schema
    tags: _containers.ScalarMap[str, str]
    storage_path: str
    status: ModelArtifactStatus
    created_at: _timestamp_pb2.Timestamp
    updated_at: _timestamp_pb2.Timestamp
    model_file_path: str
    model_config_file_path: str
    artifact_files: _containers.RepeatedScalarFieldContainer[str]
    environments: _containers.RepeatedScalarFieldContainer[str]
    created_by: _principal__client_pb2.Principal
    created_by_principal: _principal__client_pb2.PrincipalBasic
    def __init__(self, id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., name: _Optional[str] = ..., type: _Optional[_Union[ModelType, str]] = ..., description: _Optional[str] = ..., file_hashes: _Optional[_Mapping[str, str]] = ..., input_schema: _Optional[_Union[_schema__client_pb2.Schema, _Mapping]] = ..., output_schema: _Optional[_Union[_schema__client_pb2.Schema, _Mapping]] = ..., tags: _Optional[_Mapping[str, str]] = ..., storage_path: _Optional[str] = ..., status: _Optional[_Union[ModelArtifactStatus, str]] = ..., created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., updated_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., model_file_path: _Optional[str] = ..., model_config_file_path: _Optional[str] = ..., artifact_files: _Optional[_Iterable[str]] = ..., environments: _Optional[_Iterable[str]] = ..., created_by: _Optional[_Union[_principal__client_pb2.Principal, _Mapping]] = ..., created_by_principal: _Optional[_Union[_principal__client_pb2.PrincipalBasic, _Mapping]] = ...) -> None: ...

class ModelInfo(_message.Message):
    __slots__ = ["id", "name", "model_public_uri", "metadata_public_uri"]
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_PUBLIC_URI_FIELD_NUMBER: _ClassVar[int]
    METADATA_PUBLIC_URI_FIELD_NUMBER: _ClassVar[int]
    id: _id__client_pb2.Id
    name: str
    model_public_uri: str
    metadata_public_uri: str
    def __init__(self, id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., name: _Optional[str] = ..., model_public_uri: _Optional[str] = ..., metadata_public_uri: _Optional[str] = ...) -> None: ...
