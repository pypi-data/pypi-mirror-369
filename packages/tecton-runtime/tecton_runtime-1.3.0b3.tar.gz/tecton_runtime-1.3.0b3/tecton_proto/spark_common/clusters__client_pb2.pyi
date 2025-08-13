from google.protobuf import struct_pb2 as _struct_pb2
from tecton_proto.common import python_version__client_pb2 as _python_version__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class AwsAvailability(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNKNOWN_AWS_AVAILABILITY: _ClassVar[AwsAvailability]
    SPOT: _ClassVar[AwsAvailability]
    ON_DEMAND: _ClassVar[AwsAvailability]
    SPOT_WITH_FALLBACK: _ClassVar[AwsAvailability]
    INSTANCE_FLEET_FOR_INTEGRATION_TESTS_ONLY: _ClassVar[AwsAvailability]

class EbsVolumeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    UNKNOWN_EBS_VOLUME_TYPE: _ClassVar[EbsVolumeType]
    GENERAL_PURPOSE_SSD: _ClassVar[EbsVolumeType]
    THROUGHPUT_OPTIMIZED_HDD: _ClassVar[EbsVolumeType]
UNKNOWN_AWS_AVAILABILITY: AwsAvailability
SPOT: AwsAvailability
ON_DEMAND: AwsAvailability
SPOT_WITH_FALLBACK: AwsAvailability
INSTANCE_FLEET_FOR_INTEGRATION_TESTS_ONLY: AwsAvailability
UNKNOWN_EBS_VOLUME_TYPE: EbsVolumeType
GENERAL_PURPOSE_SSD: EbsVolumeType
THROUGHPUT_OPTIMIZED_HDD: EbsVolumeType

class ExistingCluster(_message.Message):
    __slots__ = ["cluster_id"]
    CLUSTER_ID_FIELD_NUMBER: _ClassVar[int]
    cluster_id: str
    def __init__(self, cluster_id: _Optional[str] = ...) -> None: ...

class DockerImage(_message.Message):
    __slots__ = ["url"]
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class NewCluster(_message.Message):
    __slots__ = ["num_workers", "autoscale", "cluster_name", "spark_version", "spark_conf", "aws_attributes", "node_type_id", "enable_elastic_disk", "init_scripts", "cluster_log_conf", "custom_tags", "terminateOnComplete", "spark_env_vars", "gcp_attributes", "json_cluster_config", "policy_id", "apply_policy_default_values", "driver_node_type_id", "root_volume_size_in_gb", "python_version", "data_security_mode", "single_user_name", "instance_pool_id", "docker_image", "enable_iceberg"]
    class SparkConfEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class SparkEnvVarsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NUM_WORKERS_FIELD_NUMBER: _ClassVar[int]
    AUTOSCALE_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_NAME_FIELD_NUMBER: _ClassVar[int]
    SPARK_VERSION_FIELD_NUMBER: _ClassVar[int]
    SPARK_CONF_FIELD_NUMBER: _ClassVar[int]
    AWS_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    NODE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    ENABLE_ELASTIC_DISK_FIELD_NUMBER: _ClassVar[int]
    INIT_SCRIPTS_FIELD_NUMBER: _ClassVar[int]
    CLUSTER_LOG_CONF_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_TAGS_FIELD_NUMBER: _ClassVar[int]
    TERMINATEONCOMPLETE_FIELD_NUMBER: _ClassVar[int]
    SPARK_ENV_VARS_FIELD_NUMBER: _ClassVar[int]
    GCP_ATTRIBUTES_FIELD_NUMBER: _ClassVar[int]
    JSON_CLUSTER_CONFIG_FIELD_NUMBER: _ClassVar[int]
    POLICY_ID_FIELD_NUMBER: _ClassVar[int]
    APPLY_POLICY_DEFAULT_VALUES_FIELD_NUMBER: _ClassVar[int]
    DRIVER_NODE_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    ROOT_VOLUME_SIZE_IN_GB_FIELD_NUMBER: _ClassVar[int]
    PYTHON_VERSION_FIELD_NUMBER: _ClassVar[int]
    DATA_SECURITY_MODE_FIELD_NUMBER: _ClassVar[int]
    SINGLE_USER_NAME_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_POOL_ID_FIELD_NUMBER: _ClassVar[int]
    DOCKER_IMAGE_FIELD_NUMBER: _ClassVar[int]
    ENABLE_ICEBERG_FIELD_NUMBER: _ClassVar[int]
    num_workers: int
    autoscale: AutoScale
    cluster_name: str
    spark_version: str
    spark_conf: _containers.ScalarMap[str, str]
    aws_attributes: AwsAttributes
    node_type_id: str
    enable_elastic_disk: bool
    init_scripts: _containers.RepeatedCompositeFieldContainer[ResourceLocation]
    cluster_log_conf: ResourceLocation
    custom_tags: _containers.RepeatedCompositeFieldContainer[ClusterTag]
    terminateOnComplete: bool
    spark_env_vars: _containers.ScalarMap[str, str]
    gcp_attributes: GCPAttributes
    json_cluster_config: _struct_pb2.Struct
    policy_id: str
    apply_policy_default_values: bool
    driver_node_type_id: str
    root_volume_size_in_gb: int
    python_version: _python_version__client_pb2.PythonVersion
    data_security_mode: str
    single_user_name: str
    instance_pool_id: str
    docker_image: DockerImage
    enable_iceberg: bool
    def __init__(self, num_workers: _Optional[int] = ..., autoscale: _Optional[_Union[AutoScale, _Mapping]] = ..., cluster_name: _Optional[str] = ..., spark_version: _Optional[str] = ..., spark_conf: _Optional[_Mapping[str, str]] = ..., aws_attributes: _Optional[_Union[AwsAttributes, _Mapping]] = ..., node_type_id: _Optional[str] = ..., enable_elastic_disk: bool = ..., init_scripts: _Optional[_Iterable[_Union[ResourceLocation, _Mapping]]] = ..., cluster_log_conf: _Optional[_Union[ResourceLocation, _Mapping]] = ..., custom_tags: _Optional[_Iterable[_Union[ClusterTag, _Mapping]]] = ..., terminateOnComplete: bool = ..., spark_env_vars: _Optional[_Mapping[str, str]] = ..., gcp_attributes: _Optional[_Union[GCPAttributes, _Mapping]] = ..., json_cluster_config: _Optional[_Union[_struct_pb2.Struct, _Mapping]] = ..., policy_id: _Optional[str] = ..., apply_policy_default_values: bool = ..., driver_node_type_id: _Optional[str] = ..., root_volume_size_in_gb: _Optional[int] = ..., python_version: _Optional[_Union[_python_version__client_pb2.PythonVersion, str]] = ..., data_security_mode: _Optional[str] = ..., single_user_name: _Optional[str] = ..., instance_pool_id: _Optional[str] = ..., docker_image: _Optional[_Union[DockerImage, _Mapping]] = ..., enable_iceberg: bool = ...) -> None: ...

class ClusterInfo(_message.Message):
    __slots__ = ["new_cluster", "final_json", "warnings"]
    NEW_CLUSTER_FIELD_NUMBER: _ClassVar[int]
    FINAL_JSON_FIELD_NUMBER: _ClassVar[int]
    WARNINGS_FIELD_NUMBER: _ClassVar[int]
    new_cluster: NewCluster
    final_json: str
    warnings: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, new_cluster: _Optional[_Union[NewCluster, _Mapping]] = ..., final_json: _Optional[str] = ..., warnings: _Optional[_Iterable[str]] = ...) -> None: ...

class AutoScale(_message.Message):
    __slots__ = ["min_workers", "max_workers"]
    MIN_WORKERS_FIELD_NUMBER: _ClassVar[int]
    MAX_WORKERS_FIELD_NUMBER: _ClassVar[int]
    min_workers: int
    max_workers: int
    def __init__(self, min_workers: _Optional[int] = ..., max_workers: _Optional[int] = ...) -> None: ...

class AwsAttributes(_message.Message):
    __slots__ = ["first_on_demand", "availability", "zone_id", "spot_bid_price_percent", "instance_profile_arn", "ebs_volume_type", "ebs_volume_count", "ebs_volume_size"]
    FIRST_ON_DEMAND_FIELD_NUMBER: _ClassVar[int]
    AVAILABILITY_FIELD_NUMBER: _ClassVar[int]
    ZONE_ID_FIELD_NUMBER: _ClassVar[int]
    SPOT_BID_PRICE_PERCENT_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_PROFILE_ARN_FIELD_NUMBER: _ClassVar[int]
    EBS_VOLUME_TYPE_FIELD_NUMBER: _ClassVar[int]
    EBS_VOLUME_COUNT_FIELD_NUMBER: _ClassVar[int]
    EBS_VOLUME_SIZE_FIELD_NUMBER: _ClassVar[int]
    first_on_demand: int
    availability: AwsAvailability
    zone_id: str
    spot_bid_price_percent: int
    instance_profile_arn: str
    ebs_volume_type: EbsVolumeType
    ebs_volume_count: int
    ebs_volume_size: int
    def __init__(self, first_on_demand: _Optional[int] = ..., availability: _Optional[_Union[AwsAvailability, str]] = ..., zone_id: _Optional[str] = ..., spot_bid_price_percent: _Optional[int] = ..., instance_profile_arn: _Optional[str] = ..., ebs_volume_type: _Optional[_Union[EbsVolumeType, str]] = ..., ebs_volume_count: _Optional[int] = ..., ebs_volume_size: _Optional[int] = ...) -> None: ...

class ResourceLocation(_message.Message):
    __slots__ = ["s3", "dbfs", "workspace", "local"]
    S3_FIELD_NUMBER: _ClassVar[int]
    DBFS_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    LOCAL_FIELD_NUMBER: _ClassVar[int]
    s3: S3StorageInfo
    dbfs: DbfsStorageInfo
    workspace: WorkspaceStorageInfo
    local: LocalStorageInfo
    def __init__(self, s3: _Optional[_Union[S3StorageInfo, _Mapping]] = ..., dbfs: _Optional[_Union[DbfsStorageInfo, _Mapping]] = ..., workspace: _Optional[_Union[WorkspaceStorageInfo, _Mapping]] = ..., local: _Optional[_Union[LocalStorageInfo, _Mapping]] = ...) -> None: ...

class S3StorageInfo(_message.Message):
    __slots__ = ["destination", "region"]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    destination: str
    region: str
    def __init__(self, destination: _Optional[str] = ..., region: _Optional[str] = ...) -> None: ...

class DbfsStorageInfo(_message.Message):
    __slots__ = ["destination"]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    destination: str
    def __init__(self, destination: _Optional[str] = ...) -> None: ...

class WorkspaceStorageInfo(_message.Message):
    __slots__ = ["destination"]
    DESTINATION_FIELD_NUMBER: _ClassVar[int]
    destination: str
    def __init__(self, destination: _Optional[str] = ...) -> None: ...

class LocalStorageInfo(_message.Message):
    __slots__ = ["path"]
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class ClusterLogConf(_message.Message):
    __slots__ = ["s3"]
    S3_FIELD_NUMBER: _ClassVar[int]
    s3: S3StorageInfo
    def __init__(self, s3: _Optional[_Union[S3StorageInfo, _Mapping]] = ...) -> None: ...

class ClusterTag(_message.Message):
    __slots__ = ["key", "value"]
    KEY_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    key: str
    value: str
    def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...

class GCPAttributes(_message.Message):
    __slots__ = ["use_preemptible_executors", "google_service_account", "boot_disk_size", "availability", "zone_id"]
    USE_PREEMPTIBLE_EXECUTORS_FIELD_NUMBER: _ClassVar[int]
    GOOGLE_SERVICE_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    BOOT_DISK_SIZE_FIELD_NUMBER: _ClassVar[int]
    AVAILABILITY_FIELD_NUMBER: _ClassVar[int]
    ZONE_ID_FIELD_NUMBER: _ClassVar[int]
    use_preemptible_executors: bool
    google_service_account: str
    boot_disk_size: int
    availability: str
    zone_id: str
    def __init__(self, use_preemptible_executors: bool = ..., google_service_account: _Optional[str] = ..., boot_disk_size: _Optional[int] = ..., availability: _Optional[str] = ..., zone_id: _Optional[str] = ...) -> None: ...
