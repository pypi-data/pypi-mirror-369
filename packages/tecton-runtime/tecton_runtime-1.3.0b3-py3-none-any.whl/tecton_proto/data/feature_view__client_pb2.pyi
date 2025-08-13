from google.protobuf import duration_pb2 as _duration_pb2
from google.protobuf import timestamp_pb2 as _timestamp_pb2
from tecton_proto.args import feature_view__client_pb2 as _feature_view__client_pb2
from tecton_proto.args import pipeline__client_pb2 as _pipeline__client_pb2
from tecton_proto.args import transformation__client_pb2 as _transformation__client_pb2
from tecton_proto.args import user_defined_function__client_pb2 as _user_defined_function__client_pb2
from tecton_proto.common import aggregation_function__client_pb2 as _aggregation_function__client_pb2
from tecton_proto.common import calculation_node__client_pb2 as _calculation_node__client_pb2
from tecton_proto.common import compute_mode__client_pb2 as _compute_mode__client_pb2
from tecton_proto.common import data_source_type__client_pb2 as _data_source_type__client_pb2
from tecton_proto.common import framework_version__client_pb2 as _framework_version__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import schema__client_pb2 as _schema__client_pb2
from tecton_proto.common import secret__client_pb2 as _secret__client_pb2
from tecton_proto.common import time_window__client_pb2 as _time_window__client_pb2
from tecton_proto.data import fco_metadata__client_pb2 as _fco_metadata__client_pb2
from tecton_proto.data import fv_materialization__client_pb2 as _fv_materialization__client_pb2
from tecton_proto.data import realtime_compute__client_pb2 as _realtime_compute__client_pb2
from tecton_proto.modelartifactservice import model_artifact_data__client_pb2 as _model_artifact_data__client_pb2
from tecton_proto.validation import validator__client_pb2 as _validator__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class ParquetOfflineStoreVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    PARQUET_OFFLINE_STORE_VERSION_UNSPECIFIED: _ClassVar[ParquetOfflineStoreVersion]
    PARQUET_OFFLINE_STORE_VERSION_1: _ClassVar[ParquetOfflineStoreVersion]
    PARQUET_OFFLINE_STORE_VERSION_2: _ClassVar[ParquetOfflineStoreVersion]

class DeltaOfflineStoreVersion(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    DELTA_OFFLINE_STORE_VERSION_UNSPECIFIED: _ClassVar[DeltaOfflineStoreVersion]
    DELTA_OFFLINE_STORE_VERSION_1: _ClassVar[DeltaOfflineStoreVersion]
    DELTA_OFFLINE_STORE_VERSION_2: _ClassVar[DeltaOfflineStoreVersion]

class MaterializationTimeRangePolicy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    MATERIALIZATION_TIME_RANGE_POLICY_UNSPECIFIED: _ClassVar[MaterializationTimeRangePolicy]
    MATERIALIZATION_TIME_RANGE_POLICY_FAIL_IF_OUT_OF_RANGE: _ClassVar[MaterializationTimeRangePolicy]
    MATERIALIZATION_TIME_RANGE_POLICY_FILTER_TO_RANGE: _ClassVar[MaterializationTimeRangePolicy]
PARQUET_OFFLINE_STORE_VERSION_UNSPECIFIED: ParquetOfflineStoreVersion
PARQUET_OFFLINE_STORE_VERSION_1: ParquetOfflineStoreVersion
PARQUET_OFFLINE_STORE_VERSION_2: ParquetOfflineStoreVersion
DELTA_OFFLINE_STORE_VERSION_UNSPECIFIED: DeltaOfflineStoreVersion
DELTA_OFFLINE_STORE_VERSION_1: DeltaOfflineStoreVersion
DELTA_OFFLINE_STORE_VERSION_2: DeltaOfflineStoreVersion
MATERIALIZATION_TIME_RANGE_POLICY_UNSPECIFIED: MaterializationTimeRangePolicy
MATERIALIZATION_TIME_RANGE_POLICY_FAIL_IF_OUT_OF_RANGE: MaterializationTimeRangePolicy
MATERIALIZATION_TIME_RANGE_POLICY_FILTER_TO_RANGE: MaterializationTimeRangePolicy

class FeatureView(_message.Message):
    __slots__ = ["feature_view_id", "fco_metadata", "entity_ids", "join_keys", "schemas", "enrichments", "temporal_aggregate", "temporal", "realtime_feature_view", "feature_table", "prompt", "timestamp_key", "online_serving_index", "pipeline", "materialization_params", "materialization_enabled", "materialization_state_transitions", "monitoring_params", "feature_store_format_version", "snowflake_data", "framework_version", "fw_version", "web_url", "batch_trigger", "validation_args", "data_quality_config", "options", "batch_compute_mode", "cache_config", "context_parameter_name", "secrets", "resource_providers"]
    class OptionsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class SecretsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _secret__client_pb2.SecretReference
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_secret__client_pb2.SecretReference, _Mapping]] = ...) -> None: ...
    class ResourceProvidersEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _id__client_pb2.Id
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ...) -> None: ...
    FEATURE_VIEW_ID_FIELD_NUMBER: _ClassVar[int]
    FCO_METADATA_FIELD_NUMBER: _ClassVar[int]
    ENTITY_IDS_FIELD_NUMBER: _ClassVar[int]
    JOIN_KEYS_FIELD_NUMBER: _ClassVar[int]
    SCHEMAS_FIELD_NUMBER: _ClassVar[int]
    ENRICHMENTS_FIELD_NUMBER: _ClassVar[int]
    TEMPORAL_AGGREGATE_FIELD_NUMBER: _ClassVar[int]
    TEMPORAL_FIELD_NUMBER: _ClassVar[int]
    REALTIME_FEATURE_VIEW_FIELD_NUMBER: _ClassVar[int]
    FEATURE_TABLE_FIELD_NUMBER: _ClassVar[int]
    PROMPT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_KEY_FIELD_NUMBER: _ClassVar[int]
    ONLINE_SERVING_INDEX_FIELD_NUMBER: _ClassVar[int]
    PIPELINE_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_PARAMS_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_STATE_TRANSITIONS_FIELD_NUMBER: _ClassVar[int]
    MONITORING_PARAMS_FIELD_NUMBER: _ClassVar[int]
    FEATURE_STORE_FORMAT_VERSION_FIELD_NUMBER: _ClassVar[int]
    SNOWFLAKE_DATA_FIELD_NUMBER: _ClassVar[int]
    FRAMEWORK_VERSION_FIELD_NUMBER: _ClassVar[int]
    FW_VERSION_FIELD_NUMBER: _ClassVar[int]
    WEB_URL_FIELD_NUMBER: _ClassVar[int]
    BATCH_TRIGGER_FIELD_NUMBER: _ClassVar[int]
    VALIDATION_ARGS_FIELD_NUMBER: _ClassVar[int]
    DATA_QUALITY_CONFIG_FIELD_NUMBER: _ClassVar[int]
    OPTIONS_FIELD_NUMBER: _ClassVar[int]
    BATCH_COMPUTE_MODE_FIELD_NUMBER: _ClassVar[int]
    CACHE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_PARAMETER_NAME_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    RESOURCE_PROVIDERS_FIELD_NUMBER: _ClassVar[int]
    feature_view_id: _id__client_pb2.Id
    fco_metadata: _fco_metadata__client_pb2.FcoMetadata
    entity_ids: _containers.RepeatedCompositeFieldContainer[_id__client_pb2.Id]
    join_keys: _containers.RepeatedScalarFieldContainer[str]
    schemas: FeatureViewSchemas
    enrichments: FeatureViewEnrichments
    temporal_aggregate: TemporalAggregate
    temporal: Temporal
    realtime_feature_view: RealtimeFeatureView
    feature_table: FeatureTable
    prompt: Prompt
    timestamp_key: str
    online_serving_index: OnlineServingIndex
    pipeline: _pipeline__client_pb2.Pipeline
    materialization_params: NewMaterializationParams
    materialization_enabled: bool
    materialization_state_transitions: _containers.RepeatedCompositeFieldContainer[MaterializationStateTransition]
    monitoring_params: MonitoringParams
    feature_store_format_version: int
    snowflake_data: SnowflakeData
    framework_version: int
    fw_version: _framework_version__client_pb2.FrameworkVersion
    web_url: str
    batch_trigger: _feature_view__client_pb2.BatchTriggerType
    validation_args: _validator__client_pb2.FeatureViewValidationArgs
    data_quality_config: DataQualityConfig
    options: _containers.ScalarMap[str, str]
    batch_compute_mode: _compute_mode__client_pb2.BatchComputeMode
    cache_config: FeatureViewCacheConfig
    context_parameter_name: str
    secrets: _containers.MessageMap[str, _secret__client_pb2.SecretReference]
    resource_providers: _containers.MessageMap[str, _id__client_pb2.Id]
    def __init__(self, feature_view_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., fco_metadata: _Optional[_Union[_fco_metadata__client_pb2.FcoMetadata, _Mapping]] = ..., entity_ids: _Optional[_Iterable[_Union[_id__client_pb2.Id, _Mapping]]] = ..., join_keys: _Optional[_Iterable[str]] = ..., schemas: _Optional[_Union[FeatureViewSchemas, _Mapping]] = ..., enrichments: _Optional[_Union[FeatureViewEnrichments, _Mapping]] = ..., temporal_aggregate: _Optional[_Union[TemporalAggregate, _Mapping]] = ..., temporal: _Optional[_Union[Temporal, _Mapping]] = ..., realtime_feature_view: _Optional[_Union[RealtimeFeatureView, _Mapping]] = ..., feature_table: _Optional[_Union[FeatureTable, _Mapping]] = ..., prompt: _Optional[_Union[Prompt, _Mapping]] = ..., timestamp_key: _Optional[str] = ..., online_serving_index: _Optional[_Union[OnlineServingIndex, _Mapping]] = ..., pipeline: _Optional[_Union[_pipeline__client_pb2.Pipeline, _Mapping]] = ..., materialization_params: _Optional[_Union[NewMaterializationParams, _Mapping]] = ..., materialization_enabled: bool = ..., materialization_state_transitions: _Optional[_Iterable[_Union[MaterializationStateTransition, _Mapping]]] = ..., monitoring_params: _Optional[_Union[MonitoringParams, _Mapping]] = ..., feature_store_format_version: _Optional[int] = ..., snowflake_data: _Optional[_Union[SnowflakeData, _Mapping]] = ..., framework_version: _Optional[int] = ..., fw_version: _Optional[_Union[_framework_version__client_pb2.FrameworkVersion, str]] = ..., web_url: _Optional[str] = ..., batch_trigger: _Optional[_Union[_feature_view__client_pb2.BatchTriggerType, str]] = ..., validation_args: _Optional[_Union[_validator__client_pb2.FeatureViewValidationArgs, _Mapping]] = ..., data_quality_config: _Optional[_Union[DataQualityConfig, _Mapping]] = ..., options: _Optional[_Mapping[str, str]] = ..., batch_compute_mode: _Optional[_Union[_compute_mode__client_pb2.BatchComputeMode, str]] = ..., cache_config: _Optional[_Union[FeatureViewCacheConfig, _Mapping]] = ..., context_parameter_name: _Optional[str] = ..., secrets: _Optional[_Mapping[str, _secret__client_pb2.SecretReference]] = ..., resource_providers: _Optional[_Mapping[str, _id__client_pb2.Id]] = ...) -> None: ...

class TemporalAggregate(_message.Message):
    __slots__ = ["slide_interval", "slide_interval_string", "features", "is_continuous", "data_source_type", "aggregation_secondary_key", "secondary_key_output_columns"]
    SLIDE_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    SLIDE_INTERVAL_STRING_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    IS_CONTINUOUS_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_SECONDARY_KEY_FIELD_NUMBER: _ClassVar[int]
    SECONDARY_KEY_OUTPUT_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    slide_interval: _duration_pb2.Duration
    slide_interval_string: str
    features: _containers.RepeatedCompositeFieldContainer[Aggregate]
    is_continuous: bool
    data_source_type: _data_source_type__client_pb2.DataSourceType
    aggregation_secondary_key: str
    secondary_key_output_columns: _containers.RepeatedCompositeFieldContainer[SecondaryKeyOutputColumn]
    def __init__(self, slide_interval: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., slide_interval_string: _Optional[str] = ..., features: _Optional[_Iterable[_Union[Aggregate, _Mapping]]] = ..., is_continuous: bool = ..., data_source_type: _Optional[_Union[_data_source_type__client_pb2.DataSourceType, str]] = ..., aggregation_secondary_key: _Optional[str] = ..., secondary_key_output_columns: _Optional[_Iterable[_Union[SecondaryKeyOutputColumn, _Mapping]]] = ...) -> None: ...

class Aggregate(_message.Message):
    __slots__ = ["input_feature_name", "output_feature_name", "function", "function_params", "window", "time_window", "batch_sawtooth_tile_size", "description", "tags"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    INPUT_FEATURE_NAME_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FEATURE_NAME_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_PARAMS_FIELD_NUMBER: _ClassVar[int]
    WINDOW_FIELD_NUMBER: _ClassVar[int]
    TIME_WINDOW_FIELD_NUMBER: _ClassVar[int]
    BATCH_SAWTOOTH_TILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    input_feature_name: str
    output_feature_name: str
    function: _aggregation_function__client_pb2.AggregationFunction
    function_params: _aggregation_function__client_pb2.AggregationFunctionParams
    window: _duration_pb2.Duration
    time_window: _time_window__client_pb2.TimeWindow
    batch_sawtooth_tile_size: _duration_pb2.Duration
    description: str
    tags: _containers.ScalarMap[str, str]
    def __init__(self, input_feature_name: _Optional[str] = ..., output_feature_name: _Optional[str] = ..., function: _Optional[_Union[_aggregation_function__client_pb2.AggregationFunction, str]] = ..., function_params: _Optional[_Union[_aggregation_function__client_pb2.AggregationFunctionParams, _Mapping]] = ..., window: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., time_window: _Optional[_Union[_time_window__client_pb2.TimeWindow, _Mapping]] = ..., batch_sawtooth_tile_size: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., description: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Attribute(_message.Message):
    __slots__ = ["column", "description", "tags"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    COLUMN_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    column: _schema__client_pb2.Field
    description: str
    tags: _containers.ScalarMap[str, str]
    def __init__(self, column: _Optional[_Union[_schema__client_pb2.Field, _Mapping]] = ..., description: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Calculation(_message.Message):
    __slots__ = ["name", "description", "tags", "abstract_syntax_tree_root", "expr"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    ABSTRACT_SYNTAX_TREE_ROOT_FIELD_NUMBER: _ClassVar[int]
    EXPR_FIELD_NUMBER: _ClassVar[int]
    name: str
    description: str
    tags: _containers.ScalarMap[str, str]
    abstract_syntax_tree_root: _calculation_node__client_pb2.AbstractSyntaxTreeNode
    expr: str
    def __init__(self, name: _Optional[str] = ..., description: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ..., abstract_syntax_tree_root: _Optional[_Union[_calculation_node__client_pb2.AbstractSyntaxTreeNode, _Mapping]] = ..., expr: _Optional[str] = ...) -> None: ...

class Embedding(_message.Message):
    __slots__ = ["input_column_name", "output_column_name", "model", "description", "tags"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    INPUT_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_COLUMN_NAME_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    input_column_name: str
    output_column_name: str
    model: str
    description: str
    tags: _containers.ScalarMap[str, str]
    def __init__(self, input_column_name: _Optional[str] = ..., output_column_name: _Optional[str] = ..., model: _Optional[str] = ..., description: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Inference(_message.Message):
    __slots__ = ["input_columns", "output_column", "model_artifact", "description", "tags"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    INPUT_COLUMNS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_COLUMN_FIELD_NUMBER: _ClassVar[int]
    MODEL_ARTIFACT_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    input_columns: _containers.RepeatedCompositeFieldContainer[_schema__client_pb2.Column]
    output_column: _schema__client_pb2.Column
    model_artifact: _model_artifact_data__client_pb2.ModelArtifactInfo
    description: str
    tags: _containers.ScalarMap[str, str]
    def __init__(self, input_columns: _Optional[_Iterable[_Union[_schema__client_pb2.Column, _Mapping]]] = ..., output_column: _Optional[_Union[_schema__client_pb2.Column, _Mapping]] = ..., model_artifact: _Optional[_Union[_model_artifact_data__client_pb2.ModelArtifactInfo, _Mapping]] = ..., description: _Optional[str] = ..., tags: _Optional[_Mapping[str, str]] = ...) -> None: ...

class TrailingTimeWindowAggregation(_message.Message):
    __slots__ = ["time_key", "aggregation_slide_period", "features", "is_continuous"]
    TIME_KEY_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_SLIDE_PERIOD_FIELD_NUMBER: _ClassVar[int]
    FEATURES_FIELD_NUMBER: _ClassVar[int]
    IS_CONTINUOUS_FIELD_NUMBER: _ClassVar[int]
    time_key: str
    aggregation_slide_period: _duration_pb2.Duration
    features: _containers.RepeatedCompositeFieldContainer[Aggregate]
    is_continuous: bool
    def __init__(self, time_key: _Optional[str] = ..., aggregation_slide_period: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., features: _Optional[_Iterable[_Union[Aggregate, _Mapping]]] = ..., is_continuous: bool = ...) -> None: ...

class Temporal(_message.Message):
    __slots__ = ["serving_ttl", "data_source_type", "backfill_config", "incremental_backfills", "is_continuous", "embeddings", "inferences", "attributes"]
    SERVING_TTL_FIELD_NUMBER: _ClassVar[int]
    DATA_SOURCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    BACKFILL_CONFIG_FIELD_NUMBER: _ClassVar[int]
    INCREMENTAL_BACKFILLS_FIELD_NUMBER: _ClassVar[int]
    IS_CONTINUOUS_FIELD_NUMBER: _ClassVar[int]
    EMBEDDINGS_FIELD_NUMBER: _ClassVar[int]
    INFERENCES_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    serving_ttl: _duration_pb2.Duration
    data_source_type: _data_source_type__client_pb2.DataSourceType
    backfill_config: _feature_view__client_pb2.BackfillConfig
    incremental_backfills: bool
    is_continuous: bool
    embeddings: _containers.RepeatedCompositeFieldContainer[Embedding]
    inferences: _containers.RepeatedCompositeFieldContainer[Inference]
    attributes: _containers.RepeatedCompositeFieldContainer[Attribute]
    def __init__(self, serving_ttl: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., data_source_type: _Optional[_Union[_data_source_type__client_pb2.DataSourceType, str]] = ..., backfill_config: _Optional[_Union[_feature_view__client_pb2.BackfillConfig, _Mapping]] = ..., incremental_backfills: bool = ..., is_continuous: bool = ..., embeddings: _Optional[_Iterable[_Union[Embedding, _Mapping]]] = ..., inferences: _Optional[_Iterable[_Union[Inference, _Mapping]]] = ..., attributes: _Optional[_Iterable[_Union[Attribute, _Mapping]]] = ...) -> None: ...

class FeatureTable(_message.Message):
    __slots__ = ["online_enabled", "offline_enabled", "serving_ttl", "attributes"]
    ONLINE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SERVING_TTL_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    online_enabled: bool
    offline_enabled: bool
    serving_ttl: _duration_pb2.Duration
    attributes: _containers.RepeatedCompositeFieldContainer[Attribute]
    def __init__(self, online_enabled: bool = ..., offline_enabled: bool = ..., serving_ttl: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., attributes: _Optional[_Iterable[_Union[Attribute, _Mapping]]] = ...) -> None: ...

class RealtimeFeatureView(_message.Message):
    __slots__ = ["no_op", "supported_environments", "required_packages", "attributes", "calculations"]
    NO_OP_FIELD_NUMBER: _ClassVar[int]
    SUPPORTED_ENVIRONMENTS_FIELD_NUMBER: _ClassVar[int]
    REQUIRED_PACKAGES_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    CALCULATIONS_FIELD_NUMBER: _ClassVar[int]
    no_op: bool
    supported_environments: _containers.RepeatedCompositeFieldContainer[_realtime_compute__client_pb2.RemoteFunctionComputeConfig]
    required_packages: _containers.RepeatedScalarFieldContainer[str]
    attributes: _containers.RepeatedCompositeFieldContainer[Attribute]
    calculations: _containers.RepeatedCompositeFieldContainer[Calculation]
    def __init__(self, no_op: bool = ..., supported_environments: _Optional[_Iterable[_Union[_realtime_compute__client_pb2.RemoteFunctionComputeConfig, _Mapping]]] = ..., required_packages: _Optional[_Iterable[str]] = ..., attributes: _Optional[_Iterable[_Union[Attribute, _Mapping]]] = ..., calculations: _Optional[_Iterable[_Union[Calculation, _Mapping]]] = ...) -> None: ...

class Prompt(_message.Message):
    __slots__ = ["environment", "attributes"]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    environment: _realtime_compute__client_pb2.RemoteFunctionComputeConfig
    attributes: _containers.RepeatedCompositeFieldContainer[Attribute]
    def __init__(self, environment: _Optional[_Union[_realtime_compute__client_pb2.RemoteFunctionComputeConfig, _Mapping]] = ..., attributes: _Optional[_Iterable[_Union[Attribute, _Mapping]]] = ...) -> None: ...

class FeatureViewSchemas(_message.Message):
    __slots__ = ["view_schema", "is_explicit_view_schema", "materialization_schema", "online_batch_table_format"]
    VIEW_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    IS_EXPLICIT_VIEW_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_SCHEMA_FIELD_NUMBER: _ClassVar[int]
    ONLINE_BATCH_TABLE_FORMAT_FIELD_NUMBER: _ClassVar[int]
    view_schema: _schema__client_pb2.Schema
    is_explicit_view_schema: bool
    materialization_schema: _schema__client_pb2.Schema
    online_batch_table_format: _schema__client_pb2.OnlineBatchTableFormat
    def __init__(self, view_schema: _Optional[_Union[_schema__client_pb2.Schema, _Mapping]] = ..., is_explicit_view_schema: bool = ..., materialization_schema: _Optional[_Union[_schema__client_pb2.Schema, _Mapping]] = ..., online_batch_table_format: _Optional[_Union[_schema__client_pb2.OnlineBatchTableFormat, _Mapping]] = ...) -> None: ...

class OnlineServingIndex(_message.Message):
    __slots__ = ["join_keys"]
    JOIN_KEYS_FIELD_NUMBER: _ClassVar[int]
    join_keys: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, join_keys: _Optional[_Iterable[str]] = ...) -> None: ...

class MaterializationStateTransition(_message.Message):
    __slots__ = ["timestamp", "online_enabled", "offline_enabled", "feature_start_timestamp", "materialization_serial_version", "force_stream_job_restart", "tecton_runtime_version"]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    ONLINE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_ENABLED_FIELD_NUMBER: _ClassVar[int]
    FEATURE_START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_SERIAL_VERSION_FIELD_NUMBER: _ClassVar[int]
    FORCE_STREAM_JOB_RESTART_FIELD_NUMBER: _ClassVar[int]
    TECTON_RUNTIME_VERSION_FIELD_NUMBER: _ClassVar[int]
    timestamp: _timestamp_pb2.Timestamp
    online_enabled: bool
    offline_enabled: bool
    feature_start_timestamp: _timestamp_pb2.Timestamp
    materialization_serial_version: int
    force_stream_job_restart: bool
    tecton_runtime_version: str
    def __init__(self, timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., online_enabled: bool = ..., offline_enabled: bool = ..., feature_start_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., materialization_serial_version: _Optional[int] = ..., force_stream_job_restart: bool = ..., tecton_runtime_version: _Optional[str] = ...) -> None: ...

class ParquetOfflineStoreParams(_message.Message):
    __slots__ = ["time_partition_size", "version"]
    TIME_PARTITION_SIZE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    time_partition_size: _duration_pb2.Duration
    version: ParquetOfflineStoreVersion
    def __init__(self, time_partition_size: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., version: _Optional[_Union[ParquetOfflineStoreVersion, str]] = ...) -> None: ...

class DeltaOfflineStoreParams(_message.Message):
    __slots__ = ["time_partition_size", "version"]
    TIME_PARTITION_SIZE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    time_partition_size: _duration_pb2.Duration
    version: DeltaOfflineStoreVersion
    def __init__(self, time_partition_size: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., version: _Optional[_Union[DeltaOfflineStoreVersion, str]] = ...) -> None: ...

class OfflineStoreParams(_message.Message):
    __slots__ = ["parquet", "delta"]
    PARQUET_FIELD_NUMBER: _ClassVar[int]
    DELTA_FIELD_NUMBER: _ClassVar[int]
    parquet: ParquetOfflineStoreParams
    delta: DeltaOfflineStoreParams
    def __init__(self, parquet: _Optional[_Union[ParquetOfflineStoreParams, _Mapping]] = ..., delta: _Optional[_Union[DeltaOfflineStoreParams, _Mapping]] = ...) -> None: ...

class SinkConfig(_message.Message):
    __slots__ = ["name", "function", "secrets", "mode"]
    class SecretsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _secret__client_pb2.SecretReference
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_secret__client_pb2.SecretReference, _Mapping]] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    FUNCTION_FIELD_NUMBER: _ClassVar[int]
    SECRETS_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    name: str
    function: _user_defined_function__client_pb2.UserDefinedFunction
    secrets: _containers.MessageMap[str, _secret__client_pb2.SecretReference]
    mode: _transformation__client_pb2.TransformationMode
    def __init__(self, name: _Optional[str] = ..., function: _Optional[_Union[_user_defined_function__client_pb2.UserDefinedFunction, _Mapping]] = ..., secrets: _Optional[_Mapping[str, _secret__client_pb2.SecretReference]] = ..., mode: _Optional[_Union[_transformation__client_pb2.TransformationMode, str]] = ...) -> None: ...

class FeaturePublishOfflineStoreConfig(_message.Message):
    __slots__ = ["publish_features_offline", "publish_start_time", "sink_config"]
    PUBLISH_FEATURES_OFFLINE_FIELD_NUMBER: _ClassVar[int]
    PUBLISH_START_TIME_FIELD_NUMBER: _ClassVar[int]
    SINK_CONFIG_FIELD_NUMBER: _ClassVar[int]
    publish_features_offline: bool
    publish_start_time: _timestamp_pb2.Timestamp
    sink_config: SinkConfig
    def __init__(self, publish_features_offline: bool = ..., publish_start_time: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., sink_config: _Optional[_Union[SinkConfig, _Mapping]] = ...) -> None: ...

class NewMaterializationParams(_message.Message):
    __slots__ = ["schedule_interval", "materialization_start_timestamp", "feature_start_timestamp", "manual_trigger_backfill_end_timestamp", "max_backfill_interval", "writes_to_online_store", "writes_to_offline_store", "offline_store_config", "offline_store_params", "batch_materialization", "stream_materialization", "max_source_data_delay", "online_store_params", "output_stream", "time_range_policy", "online_backfill_load_type", "tecton_materialization_runtime", "feature_publish_offline_store_config", "compaction_enabled", "stream_tiling_enabled", "environment", "transform_server_group_id", "transform_server_group_name", "stream_tile_size", "aggregation_leading_edge", "batch_publish_timestamp"]
    SCHEDULE_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    FEATURE_START_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    MANUAL_TRIGGER_BACKFILL_END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    MAX_BACKFILL_INTERVAL_FIELD_NUMBER: _ClassVar[int]
    WRITES_TO_ONLINE_STORE_FIELD_NUMBER: _ClassVar[int]
    WRITES_TO_OFFLINE_STORE_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_STORE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    OFFLINE_STORE_PARAMS_FIELD_NUMBER: _ClassVar[int]
    BATCH_MATERIALIZATION_FIELD_NUMBER: _ClassVar[int]
    STREAM_MATERIALIZATION_FIELD_NUMBER: _ClassVar[int]
    MAX_SOURCE_DATA_DELAY_FIELD_NUMBER: _ClassVar[int]
    ONLINE_STORE_PARAMS_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_STREAM_FIELD_NUMBER: _ClassVar[int]
    TIME_RANGE_POLICY_FIELD_NUMBER: _ClassVar[int]
    ONLINE_BACKFILL_LOAD_TYPE_FIELD_NUMBER: _ClassVar[int]
    TECTON_MATERIALIZATION_RUNTIME_FIELD_NUMBER: _ClassVar[int]
    FEATURE_PUBLISH_OFFLINE_STORE_CONFIG_FIELD_NUMBER: _ClassVar[int]
    COMPACTION_ENABLED_FIELD_NUMBER: _ClassVar[int]
    STREAM_TILING_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_SERVER_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_SERVER_GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    STREAM_TILE_SIZE_FIELD_NUMBER: _ClassVar[int]
    AGGREGATION_LEADING_EDGE_FIELD_NUMBER: _ClassVar[int]
    BATCH_PUBLISH_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    schedule_interval: _duration_pb2.Duration
    materialization_start_timestamp: _timestamp_pb2.Timestamp
    feature_start_timestamp: _timestamp_pb2.Timestamp
    manual_trigger_backfill_end_timestamp: _timestamp_pb2.Timestamp
    max_backfill_interval: _duration_pb2.Duration
    writes_to_online_store: bool
    writes_to_offline_store: bool
    offline_store_config: _feature_view__client_pb2.OfflineFeatureStoreConfig
    offline_store_params: OfflineStoreParams
    batch_materialization: _feature_view__client_pb2.ClusterConfig
    stream_materialization: _feature_view__client_pb2.ClusterConfig
    max_source_data_delay: _duration_pb2.Duration
    online_store_params: OnlineStoreParams
    output_stream: _feature_view__client_pb2.OutputStream
    time_range_policy: MaterializationTimeRangePolicy
    online_backfill_load_type: _fv_materialization__client_pb2.OnlineBackfillLoadType
    tecton_materialization_runtime: str
    feature_publish_offline_store_config: FeaturePublishOfflineStoreConfig
    compaction_enabled: bool
    stream_tiling_enabled: bool
    environment: str
    transform_server_group_id: _id__client_pb2.Id
    transform_server_group_name: str
    stream_tile_size: _duration_pb2.Duration
    aggregation_leading_edge: _feature_view__client_pb2.AggregationLeadingEdge
    batch_publish_timestamp: str
    def __init__(self, schedule_interval: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., materialization_start_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., feature_start_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., manual_trigger_backfill_end_timestamp: _Optional[_Union[_timestamp_pb2.Timestamp, _Mapping]] = ..., max_backfill_interval: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., writes_to_online_store: bool = ..., writes_to_offline_store: bool = ..., offline_store_config: _Optional[_Union[_feature_view__client_pb2.OfflineFeatureStoreConfig, _Mapping]] = ..., offline_store_params: _Optional[_Union[OfflineStoreParams, _Mapping]] = ..., batch_materialization: _Optional[_Union[_feature_view__client_pb2.ClusterConfig, _Mapping]] = ..., stream_materialization: _Optional[_Union[_feature_view__client_pb2.ClusterConfig, _Mapping]] = ..., max_source_data_delay: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., online_store_params: _Optional[_Union[OnlineStoreParams, _Mapping]] = ..., output_stream: _Optional[_Union[_feature_view__client_pb2.OutputStream, _Mapping]] = ..., time_range_policy: _Optional[_Union[MaterializationTimeRangePolicy, str]] = ..., online_backfill_load_type: _Optional[_Union[_fv_materialization__client_pb2.OnlineBackfillLoadType, str]] = ..., tecton_materialization_runtime: _Optional[str] = ..., feature_publish_offline_store_config: _Optional[_Union[FeaturePublishOfflineStoreConfig, _Mapping]] = ..., compaction_enabled: bool = ..., stream_tiling_enabled: bool = ..., environment: _Optional[str] = ..., transform_server_group_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ..., transform_server_group_name: _Optional[str] = ..., stream_tile_size: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., aggregation_leading_edge: _Optional[_Union[_feature_view__client_pb2.AggregationLeadingEdge, str]] = ..., batch_publish_timestamp: _Optional[str] = ...) -> None: ...

class OnlineStoreParams(_message.Message):
    __slots__ = ["dynamo", "redis", "bigtable"]
    DYNAMO_FIELD_NUMBER: _ClassVar[int]
    REDIS_FIELD_NUMBER: _ClassVar[int]
    BIGTABLE_FIELD_NUMBER: _ClassVar[int]
    dynamo: DynamoDbOnlineStore
    redis: RedisOnlineStore
    bigtable: BigtableOnlineStore
    def __init__(self, dynamo: _Optional[_Union[DynamoDbOnlineStore, _Mapping]] = ..., redis: _Optional[_Union[RedisOnlineStore, _Mapping]] = ..., bigtable: _Optional[_Union[BigtableOnlineStore, _Mapping]] = ...) -> None: ...

class NullableStringList(_message.Message):
    __slots__ = ["values"]
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, values: _Optional[_Iterable[str]] = ...) -> None: ...

class DynamoDbOnlineStore(_message.Message):
    __slots__ = ["cross_account_role_arn", "cross_account_external_id", "cross_account_intermediate_role_arn", "enabled", "dbfs_credentials_path", "replica_regions"]
    CROSS_ACCOUNT_ROLE_ARN_FIELD_NUMBER: _ClassVar[int]
    CROSS_ACCOUNT_EXTERNAL_ID_FIELD_NUMBER: _ClassVar[int]
    CROSS_ACCOUNT_INTERMEDIATE_ROLE_ARN_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    DBFS_CREDENTIALS_PATH_FIELD_NUMBER: _ClassVar[int]
    REPLICA_REGIONS_FIELD_NUMBER: _ClassVar[int]
    cross_account_role_arn: str
    cross_account_external_id: str
    cross_account_intermediate_role_arn: str
    enabled: bool
    dbfs_credentials_path: str
    replica_regions: NullableStringList
    def __init__(self, cross_account_role_arn: _Optional[str] = ..., cross_account_external_id: _Optional[str] = ..., cross_account_intermediate_role_arn: _Optional[str] = ..., enabled: bool = ..., dbfs_credentials_path: _Optional[str] = ..., replica_regions: _Optional[_Union[NullableStringList, _Mapping]] = ...) -> None: ...

class RedisOnlineStore(_message.Message):
    __slots__ = ["primary_endpoint", "authentication_token", "tls_enabled", "enabled", "inject_host_sni"]
    PRIMARY_ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    AUTHENTICATION_TOKEN_FIELD_NUMBER: _ClassVar[int]
    TLS_ENABLED_FIELD_NUMBER: _ClassVar[int]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    INJECT_HOST_SNI_FIELD_NUMBER: _ClassVar[int]
    primary_endpoint: str
    authentication_token: str
    tls_enabled: bool
    enabled: bool
    inject_host_sni: bool
    def __init__(self, primary_endpoint: _Optional[str] = ..., authentication_token: _Optional[str] = ..., tls_enabled: bool = ..., enabled: bool = ..., inject_host_sni: bool = ...) -> None: ...

class BigtableOnlineStore(_message.Message):
    __slots__ = ["enabled", "project_id", "instance_id"]
    ENABLED_FIELD_NUMBER: _ClassVar[int]
    PROJECT_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    enabled: bool
    project_id: str
    instance_id: str
    def __init__(self, enabled: bool = ..., project_id: _Optional[str] = ..., instance_id: _Optional[str] = ...) -> None: ...

class MonitoringParams(_message.Message):
    __slots__ = ["user_specified", "monitor_freshness", "expected_feature_freshness", "alert_email", "grace_period_seconds"]
    USER_SPECIFIED_FIELD_NUMBER: _ClassVar[int]
    MONITOR_FRESHNESS_FIELD_NUMBER: _ClassVar[int]
    EXPECTED_FEATURE_FRESHNESS_FIELD_NUMBER: _ClassVar[int]
    ALERT_EMAIL_FIELD_NUMBER: _ClassVar[int]
    GRACE_PERIOD_SECONDS_FIELD_NUMBER: _ClassVar[int]
    user_specified: bool
    monitor_freshness: bool
    expected_feature_freshness: _duration_pb2.Duration
    alert_email: str
    grace_period_seconds: int
    def __init__(self, user_specified: bool = ..., monitor_freshness: bool = ..., expected_feature_freshness: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., alert_email: _Optional[str] = ..., grace_period_seconds: _Optional[int] = ...) -> None: ...

class FeatureViewEnrichments(_message.Message):
    __slots__ = ["fp_materialization"]
    FP_MATERIALIZATION_FIELD_NUMBER: _ClassVar[int]
    fp_materialization: _fv_materialization__client_pb2.FvMaterialization
    def __init__(self, fp_materialization: _Optional[_Union[_fv_materialization__client_pb2.FvMaterialization, _Mapping]] = ...) -> None: ...

class SnowflakeData(_message.Message):
    __slots__ = ["snowflake_view_name"]
    SNOWFLAKE_VIEW_NAME_FIELD_NUMBER: _ClassVar[int]
    snowflake_view_name: str
    def __init__(self, snowflake_view_name: _Optional[str] = ...) -> None: ...

class DataQualityConfig(_message.Message):
    __slots__ = ["data_quality_enabled", "skip_default_expectations"]
    DATA_QUALITY_ENABLED_FIELD_NUMBER: _ClassVar[int]
    SKIP_DEFAULT_EXPECTATIONS_FIELD_NUMBER: _ClassVar[int]
    data_quality_enabled: bool
    skip_default_expectations: bool
    def __init__(self, data_quality_enabled: bool = ..., skip_default_expectations: bool = ...) -> None: ...

class SecondaryKeyOutputColumn(_message.Message):
    __slots__ = ["time_window", "name"]
    TIME_WINDOW_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    time_window: _time_window__client_pb2.TimeWindow
    name: str
    def __init__(self, time_window: _Optional[_Union[_time_window__client_pb2.TimeWindow, _Mapping]] = ..., name: _Optional[str] = ...) -> None: ...

class FeatureViewCacheConfig(_message.Message):
    __slots__ = ["namespace", "cache_group_name", "max_age_seconds", "max_age_jitter", "remapped_join_keys"]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    CACHE_GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    MAX_AGE_SECONDS_FIELD_NUMBER: _ClassVar[int]
    MAX_AGE_JITTER_FIELD_NUMBER: _ClassVar[int]
    REMAPPED_JOIN_KEYS_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    cache_group_name: str
    max_age_seconds: _duration_pb2.Duration
    max_age_jitter: _duration_pb2.Duration
    remapped_join_keys: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, namespace: _Optional[str] = ..., cache_group_name: _Optional[str] = ..., max_age_seconds: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., max_age_jitter: _Optional[_Union[_duration_pb2.Duration, _Mapping]] = ..., remapped_join_keys: _Optional[_Iterable[str]] = ...) -> None: ...
