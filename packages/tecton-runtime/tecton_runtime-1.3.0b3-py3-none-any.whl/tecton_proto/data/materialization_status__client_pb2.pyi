from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import compute_identity__client_pb2 as _compute_identity__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataSourceType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    DATA_SOURCE_TYPE_UNSPECIFIED: _ClassVar[DataSourceType]
    DATA_SOURCE_TYPE_BATCH: _ClassVar[DataSourceType]
    DATA_SOURCE_TYPE_STREAM: _ClassVar[DataSourceType]
    DATA_SOURCE_TYPE_INGEST: _ClassVar[DataSourceType]
    DATA_SOURCE_TYPE_DELETION: _ClassVar[DataSourceType]
    DATA_SOURCE_TYPE_FEATURE_EXPORT: _ClassVar[DataSourceType]
    DATA_SOURCE_TYPE_DATASET_GENERATION: _ClassVar[DataSourceType]
    DATA_SOURCE_TYPE_OFFLINE_MAINTENANCE: _ClassVar[DataSourceType]

class MaterializationStatusState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    MATERIALIZATION_STATUS_STATE_UNSPECIFIED: _ClassVar[MaterializationStatusState]
    MATERIALIZATION_STATUS_STATE_SCHEDULED: _ClassVar[MaterializationStatusState]
    MATERIALIZATION_STATUS_STATE_PENDING: _ClassVar[MaterializationStatusState]
    MATERIALIZATION_STATUS_STATE_RUNNING: _ClassVar[MaterializationStatusState]
    MATERIALIZATION_STATUS_STATE_SUCCESS: _ClassVar[MaterializationStatusState]
    MATERIALIZATION_STATUS_STATE_ERROR: _ClassVar[MaterializationStatusState]
    MATERIALIZATION_STATUS_STATE_DRAINED: _ClassVar[MaterializationStatusState]
    MATERIALIZATION_STATUS_STATE_MANUAL_CANCELLATION_REQUESTED: _ClassVar[MaterializationStatusState]
    MATERIALIZATION_STATUS_STATE_MANUALLY_CANCELLED: _ClassVar[MaterializationStatusState]
DATA_SOURCE_TYPE_UNSPECIFIED: DataSourceType
DATA_SOURCE_TYPE_BATCH: DataSourceType
DATA_SOURCE_TYPE_STREAM: DataSourceType
DATA_SOURCE_TYPE_INGEST: DataSourceType
DATA_SOURCE_TYPE_DELETION: DataSourceType
DATA_SOURCE_TYPE_FEATURE_EXPORT: DataSourceType
DATA_SOURCE_TYPE_DATASET_GENERATION: DataSourceType
DATA_SOURCE_TYPE_OFFLINE_MAINTENANCE: DataSourceType
MATERIALIZATION_STATUS_STATE_UNSPECIFIED: MaterializationStatusState
MATERIALIZATION_STATUS_STATE_SCHEDULED: MaterializationStatusState
MATERIALIZATION_STATUS_STATE_PENDING: MaterializationStatusState
MATERIALIZATION_STATUS_STATE_RUNNING: MaterializationStatusState
MATERIALIZATION_STATUS_STATE_SUCCESS: MaterializationStatusState
MATERIALIZATION_STATUS_STATE_ERROR: MaterializationStatusState
MATERIALIZATION_STATUS_STATE_DRAINED: MaterializationStatusState
MATERIALIZATION_STATUS_STATE_MANUAL_CANCELLATION_REQUESTED: MaterializationStatusState
MATERIALIZATION_STATUS_STATE_MANUALLY_CANCELLED: MaterializationStatusState

class AttemptConsumptionInfo(_message.Message):
    __slots__ = ["online_rows_written", "offline_rows_written", "job_duration"]
    ONLINE_ROWS_WRITTEN_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_ROWS_WRITTEN_FIELD_NUMBER: _ClassVar[int]
    JOB_DURATION_FIELD_NUMBER: _ClassVar[int]
    online_rows_written: int
    offline_rows_written: int
    job_duration: _duration_pb2.Duration
    def __init__(self, online_rows_written: _Optional[int] = ..., offline_rows_written: _Optional[int] = ..., job_duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ...) -> None: ...

class MaterializationAttemptStatus(_message.Message):
    __slots__ = ["data_source_type", "window_start_time", "window_end_time", "feature_start_time", "feature_end_time", "materialization_state", "state_message", "termination_reason", "spot_instance_failure", "materialization_task_id", "materialization_attempt_id", "materialization_task_created_at", "attempt_number", "spark_cluster_environment_version", "tecton_runtime_version", "compute_identity", "run_page_url", "tecton_managed_attempt_id", "attempt_consumption", "attempt_created_at", "is_permanent_failure", "retry_time", "progress", "duration", "allow_forced_retry", "allow_overwrite_retry", "allow_cancel", "allow_restart", "write_to_online_feature_store", "write_to_offline_feature_store"]
    DATA_SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    WINDOW_START_TIME_FIELD_NUMBER: _ClassVar[int]
    WINDOW_END_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_START_TIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_END_TIME_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_STATE_FIELD_NUMBER: _ClassVar[int]
    STATE_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    TERMINATION_REASON_FIELD_NUMBER: _ClassVar[int]
    SPOT_INSTANCE_FAILURE_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_TASK_ID_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_ATTEMPT_ID_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_TASK_CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    ATTEMPT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    SPARK_CLUSTER_ENVIRONMENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    TECTON_RUNTIME_VERSION_FIELD_NUMBER: _ClassVar[int]
    COMPUTE_IDENTITY_FIELD_NUMBER: _ClassVar[int]
    RUN_PAGE_URL_FIELD_NUMBER: _ClassVar[int]
    TECTON_MANAGED_ATTEMPT_ID_FIELD_NUMBER: _ClassVar[int]
    ATTEMPT_CONSUMPTION_FIELD_NUMBER: _ClassVar[int]
    ATTEMPT_CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    IS_PERMANENT_FAILURE_FIELD_NUMBER: _ClassVar[int]
    RETRY_TIME_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    ALLOW_FORCED_RETRY_FIELD_NUMBER: _ClassVar[int]
    ALLOW_OVERWRITE_RETRY_FIELD_NUMBER: _ClassVar[int]
    ALLOW_CANCEL_FIELD_NUMBER: _ClassVar[int]
    ALLOW_RESTART_FIELD_NUMBER: _ClassVar[int]
    WRITE_TO_ONLINE_FEATURE_STORE_FIELD_NUMBER: _ClassVar[int]
    WRITE_TO_OFFLINE_FEATURE_STORE_FIELD_NUMBER: _ClassVar[int]
    data_source_type: DataSourceType
    window_start_time: _timestamp_pb2.Timestamp
    window_end_time: _timestamp_pb2.Timestamp
    feature_start_time: _timestamp_pb2.Timestamp
    feature_end_time: _timestamp_pb2.Timestamp
    materialization_state: MaterializationStatusState
    state_message: str
    termination_reason: str
    spot_instance_failure: bool
    materialization_task_id: _id__client_pb2.Id
    materialization_attempt_id: _id__client_pb2.Id
    materialization_task_created_at: _timestamp_pb2.Timestamp
    attempt_number: int
    spark_cluster_environment_version: int
    tecton_runtime_version: str
    compute_identity: _compute_identity__client_pb2.ComputeIdentity
    run_page_url: str
    tecton_managed_attempt_id: _id__client_pb2.Id
    attempt_consumption: AttemptConsumptionInfo
    attempt_created_at: _timestamp_pb2.Timestamp
    is_permanent_failure: bool
    retry_time: _timestamp_pb2.Timestamp
    progress: float
    duration: _duration_pb2.Duration
    allow_forced_retry: bool
    allow_overwrite_retry: bool
    allow_cancel: bool
    allow_restart: bool
    write_to_online_feature_store: bool
    write_to_offline_feature_store: bool
    def __init__(self, data_source_type: _Optional[_Union[DataSourceType, str]] = ..., window_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., window_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_end_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., materialization_state: _Optional[_Union[MaterializationStatusState, str]] = ..., state_message: _Optional[str] = ..., termination_reason: _Optional[str] = ..., spot_instance_failure: bool = ..., materialization_task_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., materialization_attempt_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., materialization_task_created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., attempt_number: _Optional[int] = ..., spark_cluster_environment_version: _Optional[int] = ..., tecton_runtime_version: _Optional[str] = ..., compute_identity: _Optional[_Union[_compute_identity__client_pb2.ComputeIdentity, _Mapping]] = ..., run_page_url: _Optional[str] = ..., tecton_managed_attempt_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., attempt_consumption: _Optional[_Union[AttemptConsumptionInfo, _Mapping]] = ..., attempt_created_at: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., is_permanent_failure: bool = ..., retry_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., progress: _Optional[float] = ..., duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., allow_forced_retry: bool = ..., allow_overwrite_retry: bool = ..., allow_cancel: bool = ..., allow_restart: bool = ..., write_to_online_feature_store: bool = ..., write_to_offline_feature_store: bool = ...) -> None: ...

class MaterializationStatus(_message.Message):
    __slots__ = ["feature_package_id", "materialization_attempts", "schedule_error_message"]
    FEATURE_PACKAGE_ID_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_ATTEMPTS_FIELD_NUMBER: _ClassVar[int]
    SCHEDULE_ERROR_MESSAGE_FIELD_NUMBER: _ClassVar[int]
    feature_package_id: _id__client_pb2.Id
    materialization_attempts: _containers.RepeatedCompositeFieldContainer[MaterializationAttemptStatus]
    schedule_error_message: str
    def __init__(self, feature_package_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., materialization_attempts: _Optional[_Iterable[_Union[MaterializationAttemptStatus, _Mapping]]] = ..., schedule_error_message: _Optional[str] = ...) -> None: ...
