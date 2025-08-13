from tecton_proto.args import basic_info__client_pb2 as _basic_info__client_pb2
from tecton_proto.args import diff_options__client_pb2 as _diff_options__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import scaling_config__client_pb2 as _scaling_config__client_pb2
from tecton_proto.common import server_group_type__client_pb2 as _server_group_type__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServerGroupArgs(_message.Message):
    __slots__ = ["server_group_id", "info", "server_group_type", "transform_server_group_args", "feature_server_group_args", "prevent_destroy", "options", "autoscaling_config", "provisioned_scaling_config"]
    class OptionsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    SERVER_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    INFO_FIELD_NUMBER: _ClassVar[int]
    SERVER_GROUP_TYPE_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_SERVER_GROUP_ARGS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVER_GROUP_ARGS_FIELD_NUMBER: _ClassVar[int]
    PREVENT_DESTROY_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    AUTOSCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    PROVISIONED_SCALING_CONFIG_FIELD_NUMBER: _ClassVar[int]
    server_group_id: _id__client_pb2.Id
    info: _basic_info__client_pb2.BasicInfo
    server_group_type: _server_group_type__client_pb2.ServerGroupType
    transform_server_group_args: TransformServerGroupArgs
    feature_server_group_args: FeatureServerGroupArgs
    prevent_destroy: bool
    options: _containers.ScalarMap[str, str]
    autoscaling_config: _scaling_config__client_pb2.AutoscalingConfig
    provisioned_scaling_config: _scaling_config__client_pb2.ProvisionedScalingConfig
    def __init__(self, server_group_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., info: _Optional[_Union[_basic_info__client_pb2.BasicInfo, _Mapping]] = ..., server_group_type: _Optional[_Union[_server_group_type__client_pb2.ServerGroupType, str]] = ..., transform_server_group_args: _Optional[_Union[TransformServerGroupArgs, _Mapping]] = ..., feature_server_group_args: _Optional[_Union[FeatureServerGroupArgs, _Mapping]] = ..., prevent_destroy: bool = ..., options: _Optional[_Mapping[str, str]] = ..., autoscaling_config: _Optional[_Union[_scaling_config__client_pb2.AutoscalingConfig, _Mapping]] = ..., provisioned_scaling_config: _Optional[_Union[_scaling_config__client_pb2.ProvisionedScalingConfig, _Mapping]] = ...) -> None: ...

class TransformServerGroupArgs(_message.Message):
    __slots__ = ["environment"]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    environment: str
    def __init__(self, environment: _Optional[str] = ...) -> None: ...

class FeatureServerGroupArgs(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ServerGroupReference(_message.Message):
    __slots__ = ["server_group_id", "name"]
    SERVER_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    server_group_id: _id__client_pb2.Id
    name: str
    def __init__(self, server_group_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., name: _Optional[str] = ...) -> None: ...
