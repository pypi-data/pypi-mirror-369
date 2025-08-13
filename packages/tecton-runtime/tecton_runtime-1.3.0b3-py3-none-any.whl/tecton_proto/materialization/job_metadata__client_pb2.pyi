from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.spark_common import clusters__client_pb2 as _clusters__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class OnlineStoreType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    ONLINE_STORE_TYPE_UNSPECIFIED: _ClassVar[OnlineStoreType]
    ONLINE_STORE_TYPE_DYNAMO: _ClassVar[OnlineStoreType]
    ONLINE_STORE_TYPE_REDIS: _ClassVar[OnlineStoreType]
    ONLINE_STORE_TYPE_BIGTABLE: _ClassVar[OnlineStoreType]

class OfflineStoreType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    OFFLINE_STORE_TYPE_UNSPECIFIED: _ClassVar[OfflineStoreType]
    OFFLINE_STORE_TYPE_S3: _ClassVar[OfflineStoreType]
    OFFLINE_STORE_TYPE_DBFS: _ClassVar[OfflineStoreType]
    OFFLINE_STORE_TYPE_GCS: _ClassVar[OfflineStoreType]

class JobMetadataTableType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    JOB_METADATA_TABLE_TYPE_UNSPECIFIED: _ClassVar[JobMetadataTableType]
    JOB_METADATA_TABLE_TYPE_DYNAMO: _ClassVar[JobMetadataTableType]
    JOB_METADATA_TABLE_TYPE_GCS: _ClassVar[JobMetadataTableType]
ONLINE_STORE_TYPE_UNSPECIFIED: OnlineStoreType
ONLINE_STORE_TYPE_DYNAMO: OnlineStoreType
ONLINE_STORE_TYPE_REDIS: OnlineStoreType
ONLINE_STORE_TYPE_BIGTABLE: OnlineStoreType
OFFLINE_STORE_TYPE_UNSPECIFIED: OfflineStoreType
OFFLINE_STORE_TYPE_S3: OfflineStoreType
OFFLINE_STORE_TYPE_DBFS: OfflineStoreType
OFFLINE_STORE_TYPE_GCS: OfflineStoreType
JOB_METADATA_TABLE_TYPE_UNSPECIFIED: JobMetadataTableType
JOB_METADATA_TABLE_TYPE_DYNAMO: JobMetadataTableType
JOB_METADATA_TABLE_TYPE_GCS: JobMetadataTableType

class JobMetadata(_message.Message):
    __slots__ = ["online_store_copier_execution_info", "spark_execution_info", "tecton_managed_info", "materialization_consumption_info"]
    ONLINE_STORE_COPIER_EXECUTION_INFO_FIELD_NUMBER: _ClassVar[int]
    SPARK_EXECUTION_INFO_FIELD_NUMBER: _ClassVar[int]
    TECTON_MANAGED_INFO_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_CONSUMPTION_INFO_FIELD_NUMBER: _ClassVar[int]
    online_store_copier_execution_info: OnlineStoreCopierExecutionInfo
    spark_execution_info: SparkJobExecutionInfo
    tecton_managed_info: TectonManagedInfo
    materialization_consumption_info: MaterializationConsumptionInfo
    def __init__(self, online_store_copier_execution_info: _Optional[_Union[OnlineStoreCopierExecutionInfo, _Mapping]] = ..., spark_execution_info: _Optional[_Union[SparkJobExecutionInfo, _Mapping]] = ..., tecton_managed_info: _Optional[_Union[TectonManagedInfo, _Mapping]] = ..., materialization_consumption_info: _Optional[_Union[MaterializationConsumptionInfo, _Mapping]] = ...) -> None: ...

class OnlineStoreCopierExecutionInfo(_message.Message):
    __slots__ = ["is_revoked"]
    IS_REVOKED_FIELD_NUMBER: _ClassVar[int]
    is_revoked: bool
    def __init__(self, is_revoked: bool = ...) -> None: ...

class SparkJobExecutionInfo(_message.Message):
    __slots__ = ["run_id", "is_revoked", "stream_handoff_synchronization_info"]
    RUN_ID_FIELD_NUMBER: _ClassVar[int]
    IS_REVOKED_FIELD_NUMBER: _ClassVar[int]
    STREAM_HANDOFF_SYNCHRONIZATION_INFO_FIELD_NUMBER: _ClassVar[int]
    run_id: str
    is_revoked: bool
    stream_handoff_synchronization_info: StreamHandoffSynchronizationInfo
    def __init__(self, run_id: _Optional[str] = ..., is_revoked: bool = ..., stream_handoff_synchronization_info: _Optional[_Union[StreamHandoffSynchronizationInfo, _Mapping]] = ...) -> None: ...

class StreamHandoffSynchronizationInfo(_message.Message):
    __slots__ = ["new_cluster_started", "stream_query_start_allowed", "query_cancellation_requested", "query_cancellation_complete"]
    NEW_CLUSTER_STARTED_FIELD_NUMBER: _ClassVar[int]
    STREAM_QUERY_START_ALLOWED_FIELD_NUMBER: _ClassVar[int]
    QUERY_CANCELLATION_REQUESTED_FIELD_NUMBER: _ClassVar[int]
    QUERY_CANCELLATION_COMPLETE_FIELD_NUMBER: _ClassVar[int]
    new_cluster_started: bool
    stream_query_start_allowed: bool
    query_cancellation_requested: bool
    query_cancellation_complete: bool
    def __init__(self, new_cluster_started: bool = ..., stream_query_start_allowed: bool = ..., query_cancellation_requested: bool = ..., query_cancellation_complete: bool = ...) -> None: ...

class MaterializationConsumptionInfo(_message.Message):
    __slots__ = ["offline_store_consumption", "online_store_consumption", "compute_consumption"]
    OFFLINE_STORE_CONSUMPTION_FIELD_NUMBER: _ClassVar[int]
    ONLINE_STORE_CONSUMPTION_FIELD_NUMBER: _ClassVar[int]
    COMPUTE_CONSUMPTION_FIELD_NUMBER: _ClassVar[int]
    offline_store_consumption: OfflineStoreWriteConsumptionInfo
    online_store_consumption: OnlineStoreWriteConsumptionInfo
    compute_consumption: ComputeConsumptionInfo
    def __init__(self, offline_store_consumption: _Optional[_Union[OfflineStoreWriteConsumptionInfo, _Mapping]] = ..., online_store_consumption: _Optional[_Union[OnlineStoreWriteConsumptionInfo, _Mapping]] = ..., compute_consumption: _Optional[_Union[ComputeConsumptionInfo, _Mapping]] = ...) -> None: ...

class OfflineStoreWriteConsumptionInfo(_message.Message):
    __slots__ = ["consumption_info", "offline_store_type"]
    class ConsumptionInfoEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: OfflineConsumptionBucket
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[OfflineConsumptionBucket, _Mapping]] = ...) -> None: ...
    CONSUMPTION_INFO_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_STORE_TYPE_FIELD_NUMBER: _ClassVar[int]
    consumption_info: _containers.MessageMap[int, OfflineConsumptionBucket]
    offline_store_type: OfflineStoreType
    def __init__(self, consumption_info: _Optional[_Mapping[int, OfflineConsumptionBucket]] = ..., offline_store_type: _Optional[_Union[OfflineStoreType, str]] = ...) -> None: ...

class OfflineConsumptionBucket(_message.Message):
    __slots__ = ["rows_written", "features_written"]
    ROWS_WRITTEN_FIELD_NUMBER: _ClassVar[int]
    FEATURES_WRITTEN_FIELD_NUMBER: _ClassVar[int]
    rows_written: int
    features_written: int
    def __init__(self, rows_written: _Optional[int] = ..., features_written: _Optional[int] = ...) -> None: ...

class OnlineStoreWriteConsumptionInfo(_message.Message):
    __slots__ = ["consumption_info", "online_store_type"]
    class ConsumptionInfoEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: int
        value: OnlineConsumptionBucket
        def __init__(self, key: _Optional[int] = ..., value: _Optional[_Union[OnlineConsumptionBucket, _Mapping]] = ...) -> None: ...
    CONSUMPTION_INFO_FIELD_NUMBER: _ClassVar[int]
    ONLINE_STORE_TYPE_FIELD_NUMBER: _ClassVar[int]
    consumption_info: _containers.MessageMap[int, OnlineConsumptionBucket]
    online_store_type: OnlineStoreType
    def __init__(self, consumption_info: _Optional[_Mapping[int, OnlineConsumptionBucket]] = ..., online_store_type: _Optional[_Union[OnlineStoreType, str]] = ...) -> None: ...

class OnlineConsumptionBucket(_message.Message):
    __slots__ = ["rows_written", "features_written"]
    ROWS_WRITTEN_FIELD_NUMBER: _ClassVar[int]
    FEATURES_WRITTEN_FIELD_NUMBER: _ClassVar[int]
    rows_written: int
    features_written: int
    def __init__(self, rows_written: _Optional[int] = ..., features_written: _Optional[int] = ...) -> None: ...

class ComputeConsumptionInfo(_message.Message):
    __slots__ = ["duration", "compute_usage"]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    COMPUTE_USAGE_FIELD_NUMBER: _ClassVar[int]
    duration: _duration_pb2.Duration
    compute_usage: _containers.RepeatedCompositeFieldContainer[ComputeUsage]
    def __init__(self, duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., compute_usage: _Optional[_Iterable[_Union[ComputeUsage, _Mapping]]] = ...) -> None: ...

class ComputeUsage(_message.Message):
    __slots__ = ["instance_availability", "instance_type", "instance_count"]
    INSTANCE_AVAILABILITY_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_COUNT_FIELD_NUMBER: _ClassVar[int]
    instance_availability: _clusters__client_pb2.AwsAvailability
    instance_type: str
    instance_count: int
    def __init__(self, instance_availability: _Optional[_Union[_clusters__client_pb2.AwsAvailability, str]] = ..., instance_type: _Optional[str] = ..., instance_count: _Optional[int] = ...) -> None: ...

class TectonManagedStage(_message.Message):
    __slots__ = ["stage_type", "state", "external_link", "progress", "description", "error_type", "error_detail", "compiled_sql_query", "duration", "start_time", "stage_id", "pid"]
    class StageType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        SNOWFLAKE: _ClassVar[TectonManagedStage.StageType]
        PYTHON: _ClassVar[TectonManagedStage.StageType]
        AGGREGATE: _ClassVar[TectonManagedStage.StageType]
        OFFLINE_STORE: _ClassVar[TectonManagedStage.StageType]
        ONLINE_STORE: _ClassVar[TectonManagedStage.StageType]
        BIGQUERY: _ClassVar[TectonManagedStage.StageType]
        BULK_LOAD: _ClassVar[TectonManagedStage.StageType]
    SNOWFLAKE: TectonManagedStage.StageType
    PYTHON: TectonManagedStage.StageType
    AGGREGATE: TectonManagedStage.StageType
    OFFLINE_STORE: TectonManagedStage.StageType
    ONLINE_STORE: TectonManagedStage.StageType
    BIGQUERY: TectonManagedStage.StageType
    BULK_LOAD: TectonManagedStage.StageType
    class State(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        STATE_UNSPECIFIED: _ClassVar[TectonManagedStage.State]
        PENDING: _ClassVar[TectonManagedStage.State]
        RUNNING: _ClassVar[TectonManagedStage.State]
        SUCCESS: _ClassVar[TectonManagedStage.State]
        ERROR: _ClassVar[TectonManagedStage.State]
        CANCELLED: _ClassVar[TectonManagedStage.State]
    STATE_UNSPECIFIED: TectonManagedStage.State
    PENDING: TectonManagedStage.State
    RUNNING: TectonManagedStage.State
    SUCCESS: TectonManagedStage.State
    ERROR: TectonManagedStage.State
    CANCELLED: TectonManagedStage.State
    class ErrorType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = []
        ERROR_TYPE_UNSPECIFIED: _ClassVar[TectonManagedStage.ErrorType]
        UNEXPECTED_ERROR: _ClassVar[TectonManagedStage.ErrorType]
        USER_ERROR: _ClassVar[TectonManagedStage.ErrorType]
    ERROR_TYPE_UNSPECIFIED: TectonManagedStage.ErrorType
    UNEXPECTED_ERROR: TectonManagedStage.ErrorType
    USER_ERROR: TectonManagedStage.ErrorType
    STAGE_TYPE_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    EXTERNAL_LINK_FIELD_NUMBER: _ClassVar[int]
    PROGRESS_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    ERROR_TYPE_FIELD_NUMBER: _ClassVar[int]
    ERROR_DETAIL_FIELD_NUMBER: _ClassVar[int]
    COMPILED_SQL_QUERY_FIELD_NUMBER: _ClassVar[int]
    DURATION_FIELD_NUMBER: _ClassVar[int]
    START_TIME_FIELD_NUMBER: _ClassVar[int]
    STAGE_ID_FIELD_NUMBER: _ClassVar[int]
    PID_FIELD_NUMBER: _ClassVar[int]
    stage_type: TectonManagedStage.StageType
    state: TectonManagedStage.State
    external_link: str
    progress: float
    description: str
    error_type: TectonManagedStage.ErrorType
    error_detail: str
    compiled_sql_query: str
    duration: _duration_pb2.Duration
    start_time: _timestamp_pb2.Timestamp
    stage_id: _id__client_pb2.Id
    pid: int
    def __init__(self, stage_type: _Optional[_Union[TectonManagedStage.StageType, str]] = ..., state: _Optional[_Union[TectonManagedStage.State, str]] = ..., external_link: _Optional[str] = ..., progress: _Optional[float] = ..., description: _Optional[str] = ..., error_type: _Optional[_Union[TectonManagedStage.ErrorType, str]] = ..., error_detail: _Optional[str] = ..., compiled_sql_query: _Optional[str] = ..., duration: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., stage_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., pid: _Optional[int] = ...) -> None: ...

class TectonManagedInfo(_message.Message):
    __slots__ = ["stages", "state"]
    STAGES_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    stages: _containers.RepeatedCompositeFieldContainer[TectonManagedStage]
    state: TectonManagedStage.State
    def __init__(self, stages: _Optional[_Iterable[_Union[TectonManagedStage, _Mapping]]] = ..., state: _Optional[_Union[TectonManagedStage.State, str]] = ...) -> None: ...
