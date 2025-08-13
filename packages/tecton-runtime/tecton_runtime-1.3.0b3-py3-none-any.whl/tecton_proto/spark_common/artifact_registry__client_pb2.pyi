from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ArtifactRegistry(_message.Message):
    __slots__ = ["maven_coordinates", "s3_paths", "local_paths", "system_jars"]
    class MavenCoordinatesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ArtifactPackage
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ArtifactPackage, _Mapping]] = ...) -> None: ...
    class S3PathsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ArtifactPackage
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ArtifactPackage, _Mapping]] = ...) -> None: ...
    class LocalPathsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ArtifactPackage
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ArtifactPackage, _Mapping]] = ...) -> None: ...
    class SystemJarsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: ArtifactPackage
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[ArtifactPackage, _Mapping]] = ...) -> None: ...
    MAVEN_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    S3_PATHS_FIELD_NUMBER: _ClassVar[int]
    LOCAL_PATHS_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_JARS_FIELD_NUMBER: _ClassVar[int]
    maven_coordinates: _containers.MessageMap[str, ArtifactPackage]
    s3_paths: _containers.MessageMap[str, ArtifactPackage]
    local_paths: _containers.MessageMap[str, ArtifactPackage]
    system_jars: _containers.MessageMap[str, ArtifactPackage]
    def __init__(self, maven_coordinates: _Optional[_Mapping[str, ArtifactPackage]] = ..., s3_paths: _Optional[_Mapping[str, ArtifactPackage]] = ..., local_paths: _Optional[_Mapping[str, ArtifactPackage]] = ..., system_jars: _Optional[_Mapping[str, ArtifactPackage]] = ...) -> None: ...

class ArtifactPackage(_message.Message):
    __slots__ = ["platform_versions", "default_databricks_version", "default_emr_version"]
    class PlatformVersionsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    PLATFORM_VERSIONS_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_DATABRICKS_VERSION_FIELD_NUMBER: _ClassVar[int]
    DEFAULT_EMR_VERSION_FIELD_NUMBER: _ClassVar[int]
    platform_versions: _containers.ScalarMap[str, str]
    default_databricks_version: str
    default_emr_version: str
    def __init__(self, platform_versions: _Optional[_Mapping[str, str]] = ..., default_databricks_version: _Optional[str] = ..., default_emr_version: _Optional[str] = ...) -> None: ...
