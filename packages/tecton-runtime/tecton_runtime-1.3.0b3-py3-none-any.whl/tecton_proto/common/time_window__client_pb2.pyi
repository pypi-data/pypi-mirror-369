from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TimeWindow(_message.Message):
    __slots__ = ["relative_time_window", "lifetime_window", "time_window_series"]
    RELATIVE_TIME_WINDOW_FIELD_NUMBER: _ClassVar[int]
    LIFETIME_WINDOW_FIELD_NUMBER: _ClassVar[int]
    TIME_WINDOW_SERIES_FIELD_NUMBER: _ClassVar[int]
    relative_time_window: RelativeTimeWindow
    lifetime_window: LifetimeWindow
    time_window_series: TimeWindowSeries
    def __init__(self, relative_time_window: _Optional[_Union[RelativeTimeWindow, _Mapping]] = ..., lifetime_window: _Optional[_Union[LifetimeWindow, _Mapping]] = ..., time_window_series: _Optional[_Union[TimeWindowSeries, _Mapping]] = ...) -> None: ...

class TimeWindowSeries(_message.Message):
    __slots__ = ["time_windows"]
    TIME_WINDOWS_FIELD_NUMBER: _ClassVar[int]
    time_windows: _containers.RepeatedCompositeFieldContainer[RelativeTimeWindow]
    def __init__(self, time_windows: _Optional[_Iterable[_Union[RelativeTimeWindow, _Mapping]]] = ...) -> None: ...

class RelativeTimeWindow(_message.Message):
    __slots__ = ["window_start", "window_end"]
    WINDOW_START_FIELD_NUMBER: _ClassVar[int]
    WINDOW_END_FIELD_NUMBER: _ClassVar[int]
    window_start: _duration_pb2.Duration
    window_end: _duration_pb2.Duration
    def __init__(self, window_start: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., window_end: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class LifetimeWindow(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...
