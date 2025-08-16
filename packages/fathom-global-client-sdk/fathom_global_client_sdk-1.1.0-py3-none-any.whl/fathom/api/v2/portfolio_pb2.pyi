from buf.validate import validate_pb2 as _validate_pb2
from fathom.api.v2 import common_pb2 as _common_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import empty_pb2 as _empty_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class TaskStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TASK_STATUS_UNSPECIFIED: _ClassVar[TaskStatus]
    TASK_STATUS_PENDING: _ClassVar[TaskStatus]
    TASK_STATUS_COMPLETE: _ClassVar[TaskStatus]
    TASK_STATUS_ERROR: _ClassVar[TaskStatus]
    TASK_STATUS_IN_PROGRESS: _ClassVar[TaskStatus]
    TASK_STATUS_EXPIRED: _ClassVar[TaskStatus]
    TASK_STATUS_QUEUED: _ClassVar[TaskStatus]
    TASK_STATUS_CANCELLED: _ClassVar[TaskStatus]
    TASK_STATUS_CANCELLING: _ClassVar[TaskStatus]
TASK_STATUS_UNSPECIFIED: TaskStatus
TASK_STATUS_PENDING: TaskStatus
TASK_STATUS_COMPLETE: TaskStatus
TASK_STATUS_ERROR: TaskStatus
TASK_STATUS_IN_PROGRESS: TaskStatus
TASK_STATUS_EXPIRED: TaskStatus
TASK_STATUS_QUEUED: TaskStatus
TASK_STATUS_CANCELLED: TaskStatus
TASK_STATUS_CANCELLING: TaskStatus

class CreatePortfolioTaskRequest(_message.Message):
    __slots__ = ("layer_ids", "metadata")
    LAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    layer_ids: _containers.RepeatedScalarFieldContainer[str]
    metadata: _common_pb2.Metadata
    def __init__(self, layer_ids: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Union[_common_pb2.Metadata, _Mapping]] = ...) -> None: ...

class CreatePortfolioTaskResponse(_message.Message):
    __slots__ = ("task_id", "upload_url")
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    UPLOAD_URL_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    upload_url: str
    def __init__(self, task_id: _Optional[str] = ..., upload_url: _Optional[str] = ...) -> None: ...

class GetPortfolioTaskStatusRequest(_message.Message):
    __slots__ = ("task_id",)
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class CancelPortfolioTaskRequest(_message.Message):
    __slots__ = ("task_id",)
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class GetPortfolioTaskStatusResponse(_message.Message):
    __slots__ = ("task_status", "download_url", "errors")
    TASK_STATUS_FIELD_NUMBER: _ClassVar[int]
    DOWNLOAD_URL_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    task_status: TaskStatus
    download_url: str
    errors: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, task_status: _Optional[_Union[TaskStatus, str]] = ..., download_url: _Optional[str] = ..., errors: _Optional[_Iterable[str]] = ...) -> None: ...

class GetPortfolioQuotaInfoResponse(_message.Message):
    __slots__ = ("used", "remaining")
    USED_FIELD_NUMBER: _ClassVar[int]
    REMAINING_FIELD_NUMBER: _ClassVar[int]
    used: int
    remaining: int
    def __init__(self, used: _Optional[int] = ..., remaining: _Optional[int] = ...) -> None: ...
