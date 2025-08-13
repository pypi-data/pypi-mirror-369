from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from typing import ClassVar as _ClassVar

DESCRIPTOR: _descriptor.FileDescriptor

class BatchComputeMode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = []
    BATCH_COMPUTE_MODE_UNSPECIFIED: _ClassVar[BatchComputeMode]
    BATCH_COMPUTE_MODE_SPARK: _ClassVar[BatchComputeMode]
    BATCH_COMPUTE_MODE_RIFT: _ClassVar[BatchComputeMode]
BATCH_COMPUTE_MODE_UNSPECIFIED: BatchComputeMode
BATCH_COMPUTE_MODE_SPARK: BatchComputeMode
BATCH_COMPUTE_MODE_RIFT: BatchComputeMode
