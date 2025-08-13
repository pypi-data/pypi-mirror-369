import grpc
from grpc_health.v1 import health
from grpc_health.v1 import health_pb2


class ELBHealthServicer(health.HealthServicer):
    """Custom health servicer that sets appropriate gRPC status codes for ELB health checks.

    AWS ELB gRPC health checks use the gRPC status code of the response rather than
    the content of the response. This is useful because the matcher for ELB target
    group health checks look at the gRPC status code when using gRPC services rather
    than the content of the response.

    This servicer ensures that:
    - SERVING status returns with OK gRPC status code
    - NOT_SERVING status returns with UNAVAILABLE gRPC status code
    - UNKNOWN status returns with UNAVAILABLE gRPC status code
    - SERVICE_UNKNOWN status returns with UNAVAILABLE gRPC status code
    """

    def Check(self, request, context):
        """Override the Check method to set appropriate gRPC status codes."""
        try:
            response = super().Check(request, context)

            if response.status == health_pb2.HealthCheckResponse.SERVING:
                return response

            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details(f"Service is not serving (status: {response.status})")
            return response

        except Exception as e:
            context.set_code(grpc.StatusCode.UNAVAILABLE)
            context.set_details(f"Health check failed: {str(e)}")

            response = health_pb2.HealthCheckResponse()
            response.status = health_pb2.HealthCheckResponse.NOT_SERVING
            return response
