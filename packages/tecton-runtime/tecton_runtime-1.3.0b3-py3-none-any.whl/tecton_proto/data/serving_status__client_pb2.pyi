from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ServingState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    SERVING_STATE_UNSPECIFIED: _ClassVar[ServingState]
    SERVING_STATE_DISABLED: _ClassVar[ServingState]
    SERVING_STATE_NOT_ENOUGH_DATA: _ClassVar[ServingState]
    SERVING_STATE_PENDING: _ClassVar[ServingState]
    SERVING_STATE_OK: _ClassVar[ServingState]
    SERVING_STATE_ERROR: _ClassVar[ServingState]
    SERVING_STATE_RUNNING: _ClassVar[ServingState]
SERVING_STATE_UNSPECIFIED: ServingState
SERVING_STATE_DISABLED: ServingState
SERVING_STATE_NOT_ENOUGH_DATA: ServingState
SERVING_STATE_PENDING: ServingState
SERVING_STATE_OK: ServingState
SERVING_STATE_ERROR: ServingState
SERVING_STATE_RUNNING: ServingState

class ServingStatus(_message.Message):
    __slots__ = ["serving_state", "errors"]
    SERVING_STATE_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    serving_state: ServingState
    errors: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, serving_state: _Optional[_Union[ServingState, str]] = ..., errors: _Optional[_Iterable[str]] = ...) -> None: ...

class StatusRange(_message.Message):
    __slots__ = ["begin_inclusive", "end_exclusive", "status"]
    BEGIN_INCLUSIVE_FIELD_NUMBER: _ClassVar[int]
    END_EXCLUSIVE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    begin_inclusive: _timestamp_pb2.Timestamp
    end_exclusive: _timestamp_pb2.Timestamp
    status: ServingStatus
    def __init__(self, begin_inclusive: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., end_exclusive: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., status: _Optional[_Union[ServingStatus, _Mapping]] = ...) -> None: ...

class FeatureViewMaterializationRanges(_message.Message):
    __slots__ = ["feature_view_id", "batch_materialization_ranges"]
    FEATURE_VIEW_ID_FIELD_NUMBER: _ClassVar[int]
    BATCH_MATERIALIZATION_RANGES_FIELD_NUMBER: _ClassVar[int]
    feature_view_id: _id__client_pb2.Id
    batch_materialization_ranges: _containers.RepeatedCompositeFieldContainer[StatusRange]
    def __init__(self, feature_view_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., batch_materialization_ranges: _Optional[_Iterable[_Union[StatusRange, _Mapping]]] = ...) -> None: ...

class ServingStatusSummary(_message.Message):
    __slots__ = ["offline_readiness_ranges", "online_readiness_ranges", "batch_materialization_ranges", "streaming_start_time", "streaming_serving_status", "most_recent_ready_time", "most_recent_batch_processing_time"]
    OFFLINE_READINESS_RANGES_FIELD_NUMBER: _ClassVar[int]
    ONLINE_READINESS_RANGES_FIELD_NUMBER: _ClassVar[int]
    BATCH_MATERIALIZATION_RANGES_FIELD_NUMBER: _ClassVar[int]
    STREAMING_START_TIME_FIELD_NUMBER: _ClassVar[int]
    STREAMING_SERVING_STATUS_FIELD_NUMBER: _ClassVar[int]
    MOST_RECENT_READY_TIME_FIELD_NUMBER: _ClassVar[int]
    MOST_RECENT_BATCH_PROCESSING_TIME_FIELD_NUMBER: _ClassVar[int]
    offline_readiness_ranges: _containers.RepeatedCompositeFieldContainer[StatusRange]
    online_readiness_ranges: _containers.RepeatedCompositeFieldContainer[StatusRange]
    batch_materialization_ranges: _containers.RepeatedCompositeFieldContainer[FeatureViewMaterializationRanges]
    streaming_start_time: _timestamp_pb2.Timestamp
    streaming_serving_status: ServingStatus
    most_recent_ready_time: _timestamp_pb2.Timestamp
    most_recent_batch_processing_time: _timestamp_pb2.Timestamp
    def __init__(self, offline_readiness_ranges: _Optional[_Iterable[_Union[StatusRange, _Mapping]]] = ..., online_readiness_ranges: _Optional[_Iterable[_Union[StatusRange, _Mapping]]] = ..., batch_materialization_ranges: _Optional[_Iterable[_Union[FeatureViewMaterializationRanges, _Mapping]]] = ..., streaming_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., streaming_serving_status: _Optional[_Union[ServingStatus, _Mapping]] = ..., most_recent_ready_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., most_recent_batch_processing_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ...) -> None: ...

class FeatureViewServingStatusSummary(_message.Message):
    __slots__ = ["feature_view_id", "serving_status_summary"]
    FEATURE_VIEW_ID_FIELD_NUMBER: _ClassVar[int]
    SERVING_STATUS_SUMMARY_FIELD_NUMBER: _ClassVar[int]
    feature_view_id: _id__client_pb2.Id
    serving_status_summary: ServingStatusSummary
    def __init__(self, feature_view_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., serving_status_summary: _Optional[_Union[ServingStatusSummary, _Mapping]] = ...) -> None: ...

class FullFeatureServiceServingSummary(_message.Message):
    __slots__ = ["feature_service_serving_status_summary", "feature_view_serving_status_summaries"]
    FEATURE_SERVICE_SERVING_STATUS_SUMMARY_FIELD_NUMBER: _ClassVar[int]
    FEATURE_VIEW_SERVING_STATUS_SUMMARIES_FIELD_NUMBER: _ClassVar[int]
    feature_service_serving_status_summary: ServingStatusSummary
    feature_view_serving_status_summaries: _containers.RepeatedCompositeFieldContainer[FeatureViewServingStatusSummary]
    def __init__(self, feature_service_serving_status_summary: _Optional[_Union[ServingStatusSummary, _Mapping]] = ..., feature_view_serving_status_summaries: _Optional[_Iterable[_Union[FeatureViewServingStatusSummary, _Mapping]]] = ...) -> None: ...
