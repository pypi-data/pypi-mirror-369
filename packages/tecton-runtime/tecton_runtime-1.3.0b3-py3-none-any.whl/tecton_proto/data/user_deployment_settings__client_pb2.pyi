from tecton_proto.common import aws_credentials__client_pb2 as _aws_credentials__client_pb2
from tecton_proto.common import secret__client_pb2 as _secret__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UserDeploymentSettings(_message.Message):
    __slots__ = ["user_deployment_settings_version", "databricks_config", "user_spark_settings", "tenant_settings"]
    USER_DEPLOYMENT_SETTINGS_VERSION_FIELD_NUMBER: _ClassVar[int]
    DATABRICKS_CONFIG_FIELD_NUMBER: _ClassVar[int]
    USER_SPARK_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    TENANT_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    user_deployment_settings_version: int
    databricks_config: DatabricksConfig
    user_spark_settings: UserSparkSettings
    tenant_settings: TenantSettingsProto
    def __init__(self, user_deployment_settings_version: _Optional[int] = ..., databricks_config: _Optional[_Union[DatabricksConfig, _Mapping]] = ..., user_spark_settings: _Optional[_Union[UserSparkSettings, _Mapping]] = ..., tenant_settings: _Optional[_Union[TenantSettingsProto, _Mapping]] = ...) -> None: ...

class DatabricksConfig(_message.Message):
    __slots__ = ["workspace_url", "api_token", "user_name", "user_display_name", "spark_version"]
    WORKSPACE_URL_FIELD_NUMBER: _ClassVar[int]
    API_TOKEN_FIELD_NUMBER: _ClassVar[int]
    USER_NAME_FIELD_NUMBER: _ClassVar[int]
    USER_DISPLAY_NAME_FIELD_NUMBER: _ClassVar[int]
    SPARK_VERSION_FIELD_NUMBER: _ClassVar[int]
    workspace_url: str
    api_token: _secret__client_pb2.Secret
    user_name: str
    user_display_name: str
    spark_version: str
    def __init__(self, workspace_url: _Optional[str] = ..., api_token: _Optional[_Union[_secret__client_pb2.Secret, _Mapping]] = ..., user_name: _Optional[str] = ..., user_display_name: _Optional[str] = ..., spark_version: _Optional[str] = ...) -> None: ...

class UserSparkSettings(_message.Message):
    __slots__ = ["instance_profile_arn", "spark_conf"]
    class SparkConfEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    INSTANCE_PROFILE_ARN_FIELD_NUMBER: _ClassVar[int]
    SPARK_CONF_FIELD_NUMBER: _ClassVar[int]
    instance_profile_arn: str
    spark_conf: _containers.ScalarMap[str, str]
    def __init__(self, instance_profile_arn: _Optional[str] = ..., spark_conf: _Optional[_Mapping[str, str]] = ...) -> None: ...

class TenantSettingsProto(_message.Message):
    __slots__ = ["chronosphere_api_key", "chronosphere_restrict_label_value", "pseudonymize_amplitude_user_name", "enable_user_editing_deployment_settings", "okta_user_group_id", "base_metadata_service_url", "base_feature_service_url", "spicedb_organization_name", "customer_facing_tenant_name", "chronosphere_tecton_cluster_name", "terraform_cluster_name", "aws_settings", "internal_tenant_name"]
    CHRONOSPHERE_API_KEY_FIELD_NUMBER: _ClassVar[int]
    CHRONOSPHERE_RESTRICT_LABEL_VALUE_FIELD_NUMBER: _ClassVar[int]
    PSEUDONYMIZE_AMPLITUDE_USER_NAME_FIELD_NUMBER: _ClassVar[int]
    ENABLE_USER_EDITING_DEPLOYMENT_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    OKTA_USER_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    BASE_METADATA_SERVICE_URL_FIELD_NUMBER: _ClassVar[int]
    BASE_FEATURE_SERVICE_URL_FIELD_NUMBER: _ClassVar[int]
    SPICEDB_ORGANIZATION_NAME_FIELD_NUMBER: _ClassVar[int]
    CUSTOMER_FACING_TENANT_NAME_FIELD_NUMBER: _ClassVar[int]
    CHRONOSPHERE_TECTON_CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    TERRAFORM_CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    AWS_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    INTERNAL_TENANT_NAME_FIELD_NUMBER: _ClassVar[int]
    chronosphere_api_key: _secret__client_pb2.Secret
    chronosphere_restrict_label_value: str
    pseudonymize_amplitude_user_name: bool
    enable_user_editing_deployment_settings: bool
    okta_user_group_id: str
    base_metadata_service_url: str
    base_feature_service_url: str
    spicedb_organization_name: str
    customer_facing_tenant_name: str
    chronosphere_tecton_cluster_name: str
    terraform_cluster_name: str
    aws_settings: AwsSettings
    internal_tenant_name: str
    def __init__(self, chronosphere_api_key: _Optional[_Union[_secret__client_pb2.Secret, _Mapping]] = ..., chronosphere_restrict_label_value: _Optional[str] = ..., pseudonymize_amplitude_user_name: bool = ..., enable_user_editing_deployment_settings: bool = ..., okta_user_group_id: _Optional[str] = ..., base_metadata_service_url: _Optional[str] = ..., base_feature_service_url: _Optional[str] = ..., spicedb_organization_name: _Optional[str] = ..., customer_facing_tenant_name: _Optional[str] = ..., chronosphere_tecton_cluster_name: _Optional[str] = ..., terraform_cluster_name: _Optional[str] = ..., aws_settings: _Optional[_Union[AwsSettings, _Mapping]] = ..., internal_tenant_name: _Optional[str] = ...) -> None: ...

class AwsSettings(_message.Message):
    __slots__ = ["dynamo_role", "dynamo_extra_tags", "compute_extra_tags", "elasticache_extra_tags", "ecr_settings", "emr_settings", "ec2_settings", "elasticache_settings", "dynamo_table_names", "object_store_locations"]
    class DynamoExtraTagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class ComputeExtraTagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class ElasticacheExtraTagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    DYNAMO_ROLE_FIELD_NUMBER: _ClassVar[int]
    DYNAMO_EXTRA_TAGS_FIELD_NUMBER: _ClassVar[int]
    COMPUTE_EXTRA_TAGS_FIELD_NUMBER: _ClassVar[int]
    ELASTICACHE_EXTRA_TAGS_FIELD_NUMBER: _ClassVar[int]
    ECR_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    EMR_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    EC2_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    ELASTICACHE_SETTINGS_FIELD_NUMBER: _ClassVar[int]
    DYNAMO_TABLE_NAMES_FIELD_NUMBER: _ClassVar[int]
    OBJECT_STORE_LOCATIONS_FIELD_NUMBER: _ClassVar[int]
    dynamo_role: _aws_credentials__client_pb2.AwsIamRole
    dynamo_extra_tags: _containers.ScalarMap[str, str]
    compute_extra_tags: _containers.ScalarMap[str, str]
    elasticache_extra_tags: _containers.ScalarMap[str, str]
    ecr_settings: EcrSettings
    emr_settings: EmrSettings
    ec2_settings: Ec2Settings
    elasticache_settings: ElasticacheSettings
    dynamo_table_names: DynamoTableNames
    object_store_locations: ObjectStoreLocations
    def __init__(self, dynamo_role: _Optional[_Union[_aws_credentials__client_pb2.AwsIamRole, _Mapping]] = ..., dynamo_extra_tags: _Optional[_Mapping[str, str]] = ..., compute_extra_tags: _Optional[_Mapping[str, str]] = ..., elasticache_extra_tags: _Optional[_Mapping[str, str]] = ..., ecr_settings: _Optional[_Union[EcrSettings, _Mapping]] = ..., emr_settings: _Optional[_Union[EmrSettings, _Mapping]] = ..., ec2_settings: _Optional[_Union[Ec2Settings, _Mapping]] = ..., elasticache_settings: _Optional[_Union[ElasticacheSettings, _Mapping]] = ..., dynamo_table_names: _Optional[_Union[DynamoTableNames, _Mapping]] = ..., object_store_locations: _Optional[_Union[ObjectStoreLocations, _Mapping]] = ...) -> None: ...

class S3Location(_message.Message):
    __slots__ = ["path", "role"]
    PATH_FIELD_NUMBER: _ClassVar[int]
    ROLE_FIELD_NUMBER: _ClassVar[int]
    path: str
    role: _aws_credentials__client_pb2.AwsIamRole
    def __init__(self, path: _Optional[str] = ..., role: _Optional[_Union[_aws_credentials__client_pb2.AwsIamRole, _Mapping]] = ...) -> None: ...

class DBFSLocation(_message.Message):
    __slots__ = ["path"]
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class GCSLocation(_message.Message):
    __slots__ = ["path"]
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class DatabricksWorkspaceFileLocation(_message.Message):
    __slots__ = ["path"]
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class ObjectStoreLocation(_message.Message):
    __slots__ = ["s3_location", "dbfs_location", "gcs_location", "workspace_location"]
    S3_LOCATION_FIELD_NUMBER: _ClassVar[int]
    DBFS_LOCATION_FIELD_NUMBER: _ClassVar[int]
    GCS_LOCATION_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_LOCATION_FIELD_NUMBER: _ClassVar[int]
    s3_location: S3Location
    dbfs_location: DBFSLocation
    gcs_location: GCSLocation
    workspace_location: DatabricksWorkspaceFileLocation
    def __init__(self, s3_location: _Optional[_Union[S3Location, _Mapping]] = ..., dbfs_location: _Optional[_Union[DBFSLocation, _Mapping]] = ..., gcs_location: _Optional[_Union[GCSLocation, _Mapping]] = ..., workspace_location: _Optional[_Union[DatabricksWorkspaceFileLocation, _Mapping]] = ...) -> None: ...

class EcrSettings(_message.Message):
    __slots__ = ["ecr_control_role"]
    ECR_CONTROL_ROLE_FIELD_NUMBER: _ClassVar[int]
    ecr_control_role: _aws_credentials__client_pb2.AwsIamRole
    def __init__(self, ecr_control_role: _Optional[_Union[_aws_credentials__client_pb2.AwsIamRole, _Mapping]] = ...) -> None: ...

class EmrSettings(_message.Message):
    __slots__ = ["emr_control_role"]
    EMR_CONTROL_ROLE_FIELD_NUMBER: _ClassVar[int]
    emr_control_role: _aws_credentials__client_pb2.AwsIamRole
    def __init__(self, emr_control_role: _Optional[_Union[_aws_credentials__client_pb2.AwsIamRole, _Mapping]] = ...) -> None: ...

class Ec2Settings(_message.Message):
    __slots__ = ["ray_cluster_manager_role", "ray_instance_profile"]
    RAY_CLUSTER_MANAGER_ROLE_FIELD_NUMBER: _ClassVar[int]
    RAY_INSTANCE_PROFILE_FIELD_NUMBER: _ClassVar[int]
    ray_cluster_manager_role: _aws_credentials__client_pb2.AwsIamRole
    ray_instance_profile: _aws_credentials__client_pb2.AwsIamRole
    def __init__(self, ray_cluster_manager_role: _Optional[_Union[_aws_credentials__client_pb2.AwsIamRole, _Mapping]] = ..., ray_instance_profile: _Optional[_Union[_aws_credentials__client_pb2.AwsIamRole, _Mapping]] = ...) -> None: ...

class ElasticacheSettings(_message.Message):
    __slots__ = ["elasticache_manager_role", "elasticache_subnet_group"]
    ELASTICACHE_MANAGER_ROLE_FIELD_NUMBER: _ClassVar[int]
    ELASTICACHE_SUBNET_GROUP_FIELD_NUMBER: _ClassVar[int]
    elasticache_manager_role: _aws_credentials__client_pb2.AwsIamRole
    elasticache_subnet_group: str
    def __init__(self, elasticache_manager_role: _Optional[_Union[_aws_credentials__client_pb2.AwsIamRole, _Mapping]] = ..., elasticache_subnet_group: _Optional[str] = ...) -> None: ...

class DynamoTableNames(_message.Message):
    __slots__ = ["data_table_prefix", "status_table_name", "job_idempotence_key_table_name", "canary_table_name", "delta_log_table_name", "metric_table_prefix", "delta_log_table_name_v2", "job_metadata_table_name"]
    DATA_TABLE_PREFIX_FIELD_NUMBER: _ClassVar[int]
    STATUS_TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    JOB_IDEMPOTENCE_KEY_TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    CANARY_TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    DELTA_LOG_TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    METRIC_TABLE_PREFIX_FIELD_NUMBER: _ClassVar[int]
    DELTA_LOG_TABLE_NAME_V2_FIELD_NUMBER: _ClassVar[int]
    JOB_METADATA_TABLE_NAME_FIELD_NUMBER: _ClassVar[int]
    data_table_prefix: str
    status_table_name: str
    job_idempotence_key_table_name: str
    canary_table_name: str
    delta_log_table_name: str
    metric_table_prefix: str
    delta_log_table_name_v2: str
    job_metadata_table_name: str
    def __init__(self, data_table_prefix: _Optional[str] = ..., status_table_name: _Optional[str] = ..., job_idempotence_key_table_name: _Optional[str] = ..., canary_table_name: _Optional[str] = ..., delta_log_table_name: _Optional[str] = ..., metric_table_prefix: _Optional[str] = ..., delta_log_table_name_v2: _Optional[str] = ..., job_metadata_table_name: _Optional[str] = ...) -> None: ...

class ObjectStoreLocations(_message.Message):
    __slots__ = ["materialization", "streaming_checkpoint", "feature_server_configuration", "feature_repo", "emr_scripts", "materialization_params", "intermediate_data", "feature_server_logging", "kafka_credentials_base", "job_metadata_table", "push_api_configuration", "data_validation", "observability_service_configuration", "system_audit_logging", "databricks_scripts", "self_serve_consumption", "custom_environment_dependencies", "feature_export", "transformation_config", "model_artifacts", "rift_logs", "transform_server_group_configuration", "realtime_logs", "rift_bootstrap_scripts", "ingest_server_group_configuration"]
    MATERIALIZATION_FIELD_NUMBER: _ClassVar[int]
    STREAMING_CHECKPOINT_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVER_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    FEATURE_REPO_FIELD_NUMBER: _ClassVar[int]
    EMR_SCRIPTS_FIELD_NUMBER: _ClassVar[int]
    MATERIALIZATION_PARAMS_FIELD_NUMBER: _ClassVar[int]
    INTERMEDIATE_DATA_FIELD_NUMBER: _ClassVar[int]
    FEATURE_SERVER_LOGGING_FIELD_NUMBER: _ClassVar[int]
    KAFKA_CREDENTIALS_BASE_FIELD_NUMBER: _ClassVar[int]
    JOB_METADATA_TABLE_FIELD_NUMBER: _ClassVar[int]
    PUSH_API_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    DATA_VALIDATION_FIELD_NUMBER: _ClassVar[int]
    OBSERVABILITY_SERVICE_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    SYSTEM_AUDIT_LOGGING_FIELD_NUMBER: _ClassVar[int]
    DATABRICKS_SCRIPTS_FIELD_NUMBER: _ClassVar[int]
    SELF_SERVE_CONSUMPTION_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_ENVIRONMENT_DEPENDENCIES_FIELD_NUMBER: _ClassVar[int]
    FEATURE_EXPORT_FIELD_NUMBER: _ClassVar[int]
    TRANSFORMATION_CONFIG_FIELD_NUMBER: _ClassVar[int]
    MODEL_ARTIFACTS_FIELD_NUMBER: _ClassVar[int]
    RIFT_LOGS_FIELD_NUMBER: _ClassVar[int]
    TRANSFORM_SERVER_GROUP_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    REALTIME_LOGS_FIELD_NUMBER: _ClassVar[int]
    RIFT_BOOTSTRAP_SCRIPTS_FIELD_NUMBER: _ClassVar[int]
    INGEST_SERVER_GROUP_CONFIGURATION_FIELD_NUMBER: _ClassVar[int]
    materialization: ObjectStoreLocation
    streaming_checkpoint: ObjectStoreLocation
    feature_server_configuration: ObjectStoreLocation
    feature_repo: ObjectStoreLocation
    emr_scripts: ObjectStoreLocation
    materialization_params: ObjectStoreLocation
    intermediate_data: ObjectStoreLocation
    feature_server_logging: ObjectStoreLocation
    kafka_credentials_base: ObjectStoreLocation
    job_metadata_table: ObjectStoreLocation
    push_api_configuration: ObjectStoreLocation
    data_validation: ObjectStoreLocation
    observability_service_configuration: ObjectStoreLocation
    system_audit_logging: ObjectStoreLocation
    databricks_scripts: ObjectStoreLocation
    self_serve_consumption: ObjectStoreLocation
    custom_environment_dependencies: ObjectStoreLocation
    feature_export: ObjectStoreLocation
    transformation_config: ObjectStoreLocation
    model_artifacts: ObjectStoreLocation
    rift_logs: ObjectStoreLocation
    transform_server_group_configuration: ObjectStoreLocation
    realtime_logs: ObjectStoreLocation
    rift_bootstrap_scripts: ObjectStoreLocation
    ingest_server_group_configuration: ObjectStoreLocation
    def __init__(self, materialization: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., streaming_checkpoint: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., feature_server_configuration: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., feature_repo: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., emr_scripts: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., materialization_params: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., intermediate_data: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., feature_server_logging: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., kafka_credentials_base: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., job_metadata_table: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., push_api_configuration: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., data_validation: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., observability_service_configuration: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., system_audit_logging: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., databricks_scripts: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., self_serve_consumption: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., custom_environment_dependencies: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., feature_export: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., transformation_config: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., model_artifacts: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., rift_logs: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., transform_server_group_configuration: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., realtime_logs: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., rift_bootstrap_scripts: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ..., ingest_server_group_configuration: _Optional[_Union[ObjectStoreLocation, _Mapping]] = ...) -> None: ...
