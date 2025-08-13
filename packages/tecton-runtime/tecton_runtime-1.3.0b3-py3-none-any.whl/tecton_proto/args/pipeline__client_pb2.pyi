from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.args import diff_options__client_pb2 as _diff_options__client_pb2
from tecton_proto.args import feature_service__client_pb2 as _feature_service__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import schema__client_pb2 as _schema__client_pb2
from tecton_proto.common import spark_schema__client_pb2 as _spark_schema__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TimeReference(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    TIME_REFERENCE_UNSPECIFIED: _ClassVar[TimeReference]
    TIME_REFERENCE_MATERIALIZATION_START_TIME: _ClassVar[TimeReference]
    TIME_REFERENCE_MATERIALIZATION_END_TIME: _ClassVar[TimeReference]
    TIME_REFERENCE_UNBOUNDED_PAST: _ClassVar[TimeReference]
    TIME_REFERENCE_UNBOUNDED_FUTURE: _ClassVar[TimeReference]

class ContextType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    CONTEXT_TYPE_UNSPECIFIED: _ClassVar[ContextType]
    CONTEXT_TYPE_MATERIALIZATION: _ClassVar[ContextType]
    CONTEXT_TYPE_REALTIME: _ClassVar[ContextType]
TIME_REFERENCE_UNSPECIFIED: TimeReference
TIME_REFERENCE_MATERIALIZATION_START_TIME: TimeReference
TIME_REFERENCE_MATERIALIZATION_END_TIME: TimeReference
TIME_REFERENCE_UNBOUNDED_PAST: TimeReference
TIME_REFERENCE_UNBOUNDED_FUTURE: TimeReference
CONTEXT_TYPE_UNSPECIFIED: ContextType
CONTEXT_TYPE_MATERIALIZATION: ContextType
CONTEXT_TYPE_REALTIME: ContextType

class Pipeline(_message.Message):
    __slots__ = ["root"]
    ROOT_FIELD_NUMBER: _ClassVar[int]
    root: PipelineNode
    def __init__(self, root: _Optional[_Union[PipelineNode, _Mapping]] = ...) -> None: ...

class PipelineNode(_message.Message):
    __slots__ = ["transformation_node", "data_source_node", "constant_node", "request_data_source_node", "feature_view_node", "materialization_context_node", "context_node", "join_inputs_node"]
    TRANSFORMATION_NODE_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_NODE_FIELD_NUMBER: _ClassVar[int]
    CONSTANT_NODE_FIELD_NUMBER: _ClassVar[int]
    REQUEST_DATA_SOURCE_NODE_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_NODE_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_CONTEXT_NODE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_NODE_FIELD_NUMBER: _ClassVar[int]
    JOIN_INPUTS_NODE_FIELD_NUMBER: _ClassVar[int]
    transformation_node: TransformationNode
    data_source_node: DataSourceNode
    constant_node: ConstantNode
    request_data_source_node: RequestDataSourceNode
    feature_view_node: FeatureViewNode
    materialization_context_node: MaterializationContextNode
    context_node: ContextNode
    join_inputs_node: JoinInputsNode
    def __init__(self, transformation_node: _Optional[_Union[TransformationNode, _Mapping]] = ..., data_source_node: _Optional[_Union[DataSourceNode, _Mapping]] = ..., constant_node: _Optional[_Union[ConstantNode, _Mapping]] = ..., request_data_source_node: _Optional[_Union[RequestDataSourceNode, _Mapping]] = ..., feature_view_node: _Optional[_Union[FeatureViewNode, _Mapping]] = ..., materialization_context_node: _Optional[_Union[MaterializationContextNode, _Mapping]] = ..., context_node: _Optional[_Union[ContextNode, _Mapping]] = ..., join_inputs_node: _Optional[_Union[JoinInputsNode, _Mapping]] = ...) -> None: ...

class RequestDataSourceNode(_message.Message):
    __slots__ = ["request_context", "input_name"]
    REQUEST_CONTEXT_FIELD_NUMBER: _ClassVar[int]
    INPUT_NAME_FIELD_NUMBER: _ClassVar[int]
    request_context: RequestContext
    input_name: str
    def __init__(self, request_context: _Optional[_Union[RequestContext, _Mapping]] = ..., input_name: _Optional[str] = ...) -> None: ...

class RequestContext(_message.Message):
    __slots__ = ["tecton_schema", "schema"]
    TECTON_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    SCHEMA_FIELD_NUMBER: _ClassVar[int]
    tecton_schema: _schema__client_pb2.Schema
    schema: _spark_schema__client_pb2.SparkSchema
    def __init__(self, tecton_schema: _Optional[_Union[_schema__client_pb2.Schema, _Mapping]] = ..., schema: _Optional[_Union[_spark_schema__client_pb2.SparkSchema, _Mapping]] = ...) -> None: ...

class FeatureViewNode(_message.Message):
    __slots__ = ["feature_view_id", "feature_reference", "input_name"]
    FEATURE_VIEW_ID_FIELD_NUMBER: _ClassVar[int]
    FEATURE_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    INPUT_NAME_FIELD_NUMBER: _ClassVar[int]
    feature_view_id: _id__client_pb2.Id
    feature_reference: _feature_service__client_pb2.FeatureReference
    input_name: str
    def __init__(self, feature_view_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., feature_reference: _Optional[_Union[_feature_service__client_pb2.FeatureReference, _Mapping]] = ..., input_name: _Optional[str] = ...) -> None: ...

class TransformationNode(_message.Message):
    __slots__ = ["transformation_id", "inputs"]
    TRANSFORMATION_ID_FIELD_NUMBER: _ClassVar[int]
    INPUTS_FIELD_NUMBER: _ClassVar[int]
    transformation_id: _id__client_pb2.Id
    inputs: _containers.RepeatedCompositeFieldContainer[Input]
    def __init__(self, transformation_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., inputs: _Optional[_Iterable[_Union[Input, _Mapping]]] = ...) -> None: ...

class JoinInputsNode(_message.Message):
    __slots__ = ["nodes"]
    NODES_FIELD_NUMBER: _ClassVar[int]
    nodes: _containers.RepeatedCompositeFieldContainer[PipelineNode]
    def __init__(self, nodes: _Optional[_Iterable[_Union[PipelineNode, _Mapping]]] = ...) -> None: ...

class Input(_message.Message):
    __slots__ = ["arg_index", "arg_name", "node"]
    ARG_INDEX_FIELD_NUMBER: _ClassVar[int]
    ARG_NAME_FIELD_NUMBER: _ClassVar[int]
    NODE_FIELD_NUMBER: _ClassVar[int]
    arg_index: int
    arg_name: str
    node: PipelineNode
    def __init__(self, arg_index: _Optional[int] = ..., arg_name: _Optional[str] = ..., node: _Optional[_Union[PipelineNode, _Mapping]] = ...) -> None: ...

class DataSourceNode(_message.Message):
    __slots__ = ["virtual_data_source_id", "window", "window_unbounded_preceding", "window_unbounded", "start_time_offset", "schedule_offset", "input_name", "filter_start_time", "filter_end_time"]
    VIRTUAL_DATA_SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    WINDOW_FIELD_NUMBER: _ClassVar[int]
    WINDOW_UNBOUNDED_PRECEDING_FIELD_NUMBER: _ClassVar[int]
    WINDOW_UNBOUNDED_FIELD_NUMBER: _ClassVar[int]
    START_TIME_OFFSET_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_OFFSET_FIELD_NUMBER: _ClassVar[int]
    INPUT_NAME_FIELD_NUMBER: _ClassVar[int]
    FILTER_START_TIME_FIELD_NUMBER: _ClassVar[int]
    FILTER_END_TIME_FIELD_NUMBER: _ClassVar[int]
    virtual_data_source_id: _id__client_pb2.Id
    window: _duration_pb2.Duration
    window_unbounded_preceding: bool
    window_unbounded: bool
    start_time_offset: _duration_pb2.Duration
    schedule_offset: _duration_pb2.Duration
    input_name: str
    filter_start_time: FilterDateTime
    filter_end_time: FilterDateTime
    def __init__(self, virtual_data_source_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., window: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., window_unbounded_preceding: bool = ..., window_unbounded: bool = ..., start_time_offset: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., schedule_offset: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., input_name: _Optional[str] = ..., filter_start_time: _Optional[_Union[FilterDateTime, _Mapping]] = ..., filter_end_time: _Optional[_Union[FilterDateTime, _Mapping]] = ...) -> None: ...

class FilterDateTime(_message.Message):
    __slots__ = ["timestamp", "relative_time"]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_TIME_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    relative_time: RelativeTime
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., relative_time: _Optional[_Union[RelativeTime, _Mapping]] = ...) -> None: ...

class RelativeTime(_message.Message):
    __slots__ = ["time_reference", "offset"]
    TIME_REFERENCE_FIELD_NUMBER: _ClassVar[int]
    OFFSET_FIELD_NUMBER: _ClassVar[int]
    time_reference: TimeReference
    offset: _duration_pb2.Duration
    def __init__(self, time_reference: _Optional[_Union[TimeReference, str]] = ..., offset: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class ConstantNode(_message.Message):
    __slots__ = ["string_const", "int_const", "float_const", "bool_const", "null_const"]
    STRING_CONST_FIELD_NUMBER: _ClassVar[int]
    INT_CONST_FIELD_NUMBER: _ClassVar[int]
    FLOAT_CONST_FIELD_NUMBER: _ClassVar[int]
    BOOL_CONST_FIELD_NUMBER: _ClassVar[int]
    NULL_CONST_FIELD_NUMBER: _ClassVar[int]
    string_const: str
    int_const: str
    float_const: str
    bool_const: bool
    null_const: _empty_pb2.Empty
    def __init__(self, string_const: _Optional[str] = ..., int_const: _Optional[str] = ..., float_const: _Optional[str] = ..., bool_const: bool = ..., null_const: _Optional[_Union[_empty_pb2.Empty, _Mapping]] = ...) -> None: ...

class MaterializationContextNode(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class ContextNode(_message.Message):
    __slots__ = ["context_type", "input_name"]
    CONTEXT_TYPE_FIELD_NUMBER: _ClassVar[int]
    INPUT_NAME_FIELD_NUMBER: _ClassVar[int]
    context_type: ContextType
    input_name: str
    def __init__(self, context_type: _Optional[_Union[ContextType, str]] = ..., input_name: _Optional[str] = ...) -> None: ...
