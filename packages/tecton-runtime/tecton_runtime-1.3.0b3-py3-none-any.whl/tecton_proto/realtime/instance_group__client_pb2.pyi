from tecton_proto.common import container_image__client_pb2 as _container_image__client_pb2
from tecton_proto.common import id__client_pb2 as _id__client_pb2
from tecton_proto.common import server_group_type__client_pb2 as _server_group_type__client_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class InstanceGroup(_message.Message):
    __slots__ = ["name", "workspace", "app_name", "container_image", "capacity", "health_check_config", "health_check_name", "prometheus_port", "grpc_port", "http_port", "aws_instance_group", "google_cloud_instance_group", "tags", "environment_variables", "host", "metrics_namespace", "custom_metric_labels", "should_update_repo", "repo_upgrade_spec", "type", "server_group_id"]
    class TagsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class EnvironmentVariablesEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class CustomMetricLabelsEntry(_message.Message):
        __slots__ = ["key", "value"]
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    WORKSPACE_FIELD_NUMBER: _ClassVar[int]
    APP_NAME_FIELD_NUMBER: _ClassVar[int]
    CONTAINER_IMAGE_FIELD_NUMBER: _ClassVar[int]
    CAPACITY_FIELD_NUMBER: _ClassVar[int]
    HEALTH_CHECK_CONFIG_FIELD_NUMBER: _ClassVar[int]
    HEALTH_CHECK_NAME_FIELD_NUMBER: _ClassVar[int]
    PROMETHEUS_PORT_FIELD_NUMBER: _ClassVar[int]
    GRPC_PORT_FIELD_NUMBER: _ClassVar[int]
    HTTP_PORT_FIELD_NUMBER: _ClassVar[int]
    AWS_INSTANCE_GROUP_FIELD_NUMBER: _ClassVar[int]
    GOOGLE_CLOUD_INSTANCE_GROUP_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    ENVIRONMENT_VARIABLES_FIELD_NUMBER: _ClassVar[int]
    HOST_FIELD_NUMBER: _ClassVar[int]
    METRICS_NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    CUSTOM_METRIC_LABELS_FIELD_NUMBER: _ClassVar[int]
    SHOULD_UPDATE_REPO_FIELD_NUMBER: _ClassVar[int]
    REPO_UPGRADE_SPEC_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    SERVER_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    name: str
    workspace: str
    app_name: str
    container_image: _container_image__client_pb2.ContainerImage
    capacity: CapacityConfig
    health_check_config: HealthCheckConfig
    health_check_name: str
    prometheus_port: NamedPort
    grpc_port: NamedPort
    http_port: NamedPort
    aws_instance_group: AWSInstanceGroup
    google_cloud_instance_group: GoogleCloudInstanceGroup
    tags: _containers.ScalarMap[str, str]
    environment_variables: _containers.ScalarMap[str, str]
    host: str
    metrics_namespace: str
    custom_metric_labels: _containers.ScalarMap[str, str]
    should_update_repo: bool
    repo_upgrade_spec: str
    type: _server_group_type__client_pb2.ServerGroupType
    server_group_id: _id__client_pb2.Id
    def __init__(self, name: _Optional[str] = ..., workspace: _Optional[str] = ..., app_name: _Optional[str] = ..., container_image: _Optional[_Union[_container_image__client_pb2.ContainerImage, _Mapping]] = ..., capacity: _Optional[_Union[CapacityConfig, _Mapping]] = ..., health_check_config: _Optional[_Union[HealthCheckConfig, _Mapping]] = ..., health_check_name: _Optional[str] = ..., prometheus_port: _Optional[_Union[NamedPort, _Mapping]] = ..., grpc_port: _Optional[_Union[NamedPort, _Mapping]] = ..., http_port: _Optional[_Union[NamedPort, _Mapping]] = ..., aws_instance_group: _Optional[_Union[AWSInstanceGroup, _Mapping]] = ..., google_cloud_instance_group: _Optional[_Union[GoogleCloudInstanceGroup, _Mapping]] = ..., tags: _Optional[_Mapping[str, str]] = ..., environment_variables: _Optional[_Mapping[str, str]] = ..., host: _Optional[str] = ..., metrics_namespace: _Optional[str] = ..., custom_metric_labels: _Optional[_Mapping[str, str]] = ..., should_update_repo: bool = ..., repo_upgrade_spec: _Optional[str] = ..., type: _Optional[_Union[_server_group_type__client_pb2.ServerGroupType, str]] = ..., server_group_id: _Optional[_Union[_id__client_pb2.Id, _Mapping]] = ...) -> None: ...

class InstanceGroupHandle(_message.Message):
    __slots__ = ["instance_group_id", "instance_group_name", "instance_group_template_id"]
    INSTANCE_GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_GROUP_TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    instance_group_id: str
    instance_group_name: str
    instance_group_template_id: str
    def __init__(self, instance_group_id: _Optional[str] = ..., instance_group_name: _Optional[str] = ..., instance_group_template_id: _Optional[str] = ...) -> None: ...

class CapacityConfig(_message.Message):
    __slots__ = ["autoscaling_enabled", "min_nodes", "max_nodes", "desired_nodes"]
    AUTOSCALING_ENABLED_FIELD_NUMBER: _ClassVar[int]
    MIN_NODES_FIELD_NUMBER: _ClassVar[int]
    MAX_NODES_FIELD_NUMBER: _ClassVar[int]
    DESIRED_NODES_FIELD_NUMBER: _ClassVar[int]
    autoscaling_enabled: bool
    min_nodes: int
    max_nodes: int
    desired_nodes: int
    def __init__(self, autoscaling_enabled: bool = ..., min_nodes: _Optional[int] = ..., max_nodes: _Optional[int] = ..., desired_nodes: _Optional[int] = ...) -> None: ...

class InstanceGroupStatus(_message.Message):
    __slots__ = ["healthy_instances", "unhealthy_instances"]
    HEALTHY_INSTANCES_FIELD_NUMBER: _ClassVar[int]
    UNHEALTHY_INSTANCES_FIELD_NUMBER: _ClassVar[int]
    healthy_instances: int
    unhealthy_instances: int
    def __init__(self, healthy_instances: _Optional[int] = ..., unhealthy_instances: _Optional[int] = ...) -> None: ...

class HealthCheckConfig(_message.Message):
    __slots__ = ["port", "path", "protocol_type"]
    PORT_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    PROTOCOL_TYPE_FIELD_NUMBER: _ClassVar[int]
    port: NamedPort
    path: str
    protocol_type: str
    def __init__(self, port: _Optional[_Union[NamedPort, _Mapping]] = ..., path: _Optional[str] = ..., protocol_type: _Optional[str] = ...) -> None: ...

class NamedPort(_message.Message):
    __slots__ = ["port_number", "port_name"]
    PORT_NUMBER_FIELD_NUMBER: _ClassVar[int]
    PORT_NAME_FIELD_NUMBER: _ClassVar[int]
    port_number: int
    port_name: str
    def __init__(self, port_number: _Optional[int] = ..., port_name: _Optional[str] = ...) -> None: ...

class AWSInstanceGroup(_message.Message):
    __slots__ = ["autoscaling_group_arn", "autoscaling_group_name", "region", "port", "health_check_path", "instance_type", "ami_image_id", "iam_instance_profile_arn", "security_group_ids", "subnet_ids", "launch_template_id", "instance_warmup_time_seconds"]
    AUTOSCALING_GROUP_ARN_FIELD_NUMBER: _ClassVar[int]
    AUTOSCALING_GROUP_NAME_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    HEALTH_CHECK_PATH_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    AMI_IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    IAM_INSTANCE_PROFILE_ARN_FIELD_NUMBER: _ClassVar[int]
    SECURITY_GROUP_IDS_FIELD_NUMBER: _ClassVar[int]
    SUBNET_IDS_FIELD_NUMBER: _ClassVar[int]
    LAUNCH_TEMPLATE_ID_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_WARMUP_TIME_SECONDS_FIELD_NUMBER: _ClassVar[int]
    autoscaling_group_arn: str
    autoscaling_group_name: str
    region: str
    port: int
    health_check_path: str
    instance_type: str
    ami_image_id: str
    iam_instance_profile_arn: str
    security_group_ids: _containers.RepeatedScalarFieldContainer[str]
    subnet_ids: _containers.RepeatedScalarFieldContainer[str]
    launch_template_id: str
    instance_warmup_time_seconds: int
    def __init__(self, autoscaling_group_arn: _Optional[str] = ..., autoscaling_group_name: _Optional[str] = ..., region: _Optional[str] = ..., port: _Optional[int] = ..., health_check_path: _Optional[str] = ..., instance_type: _Optional[str] = ..., ami_image_id: _Optional[str] = ..., iam_instance_profile_arn: _Optional[str] = ..., security_group_ids: _Optional[_Iterable[str]] = ..., subnet_ids: _Optional[_Iterable[str]] = ..., launch_template_id: _Optional[str] = ..., instance_warmup_time_seconds: _Optional[int] = ...) -> None: ...

class AWSInstanceGroupUpdateConfig(_message.Message):
    __slots__ = ["instance_type", "ami_image_id"]
    INSTANCE_TYPE_FIELD_NUMBER: _ClassVar[int]
    AMI_IMAGE_ID_FIELD_NUMBER: _ClassVar[int]
    instance_type: str
    ami_image_id: str
    def __init__(self, instance_type: _Optional[str] = ..., ami_image_id: _Optional[str] = ...) -> None: ...

class AWSTargetGroup(_message.Message):
    __slots__ = ["arn", "name", "instance_group", "load_balancer_arn"]
    ARN_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_GROUP_FIELD_NUMBER: _ClassVar[int]
    LOAD_BALANCER_ARN_FIELD_NUMBER: _ClassVar[int]
    arn: str
    name: str
    instance_group: AWSInstanceGroup
    load_balancer_arn: str
    def __init__(self, arn: _Optional[str] = ..., name: _Optional[str] = ..., instance_group: _Optional[_Union[AWSInstanceGroup, _Mapping]] = ..., load_balancer_arn: _Optional[str] = ...) -> None: ...

class GoogleCloudInstanceGroup(_message.Message):
    __slots__ = ["project", "region", "target_id", "machine_type", "subnetworks", "health_check_name", "service_account", "scopes"]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    MACHINE_TYPE_FIELD_NUMBER: _ClassVar[int]
    SUBNETWORKS_FIELD_NUMBER: _ClassVar[int]
    HEALTH_CHECK_NAME_FIELD_NUMBER: _ClassVar[int]
    SERVICE_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    SCOPES_FIELD_NUMBER: _ClassVar[int]
    project: str
    region: str
    target_id: str
    machine_type: str
    subnetworks: _containers.RepeatedScalarFieldContainer[str]
    health_check_name: str
    service_account: str
    scopes: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, project: _Optional[str] = ..., region: _Optional[str] = ..., target_id: _Optional[str] = ..., machine_type: _Optional[str] = ..., subnetworks: _Optional[_Iterable[str]] = ..., health_check_name: _Optional[str] = ..., service_account: _Optional[str] = ..., scopes: _Optional[_Iterable[str]] = ...) -> None: ...

class GoogleCloudBackendService(_message.Message):
    __slots__ = ["target_id", "project", "region", "instance_group"]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    PROJECT_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    INSTANCE_GROUP_FIELD_NUMBER: _ClassVar[int]
    target_id: str
    project: str
    region: str
    instance_group: GoogleCloudInstanceGroup
    def __init__(self, target_id: _Optional[str] = ..., project: _Optional[str] = ..., region: _Optional[str] = ..., instance_group: _Optional[_Union[GoogleCloudInstanceGroup, _Mapping]] = ...) -> None: ...

class LoadBalancerTarget(_message.Message):
    __slots__ = ["aws_target_group", "google_backend_service"]
    AWS_TARGET_GROUP_FIELD_NUMBER: _ClassVar[int]
    GOOGLE_BACKEND_SERVICE_FIELD_NUMBER: _ClassVar[int]
    aws_target_group: AWSTargetGroup
    google_backend_service: GoogleCloudBackendService
    def __init__(self, aws_target_group: _Optional[_Union[AWSTargetGroup, _Mapping]] = ..., google_backend_service: _Optional[_Union[GoogleCloudBackendService, _Mapping]] = ...) -> None: ...
