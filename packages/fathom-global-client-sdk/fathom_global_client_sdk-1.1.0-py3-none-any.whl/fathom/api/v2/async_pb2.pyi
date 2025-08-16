from buf.validate import validate_pb2 as _validate_pb2
from fathom.api.v2 import common_pb2 as _common_pb2
from fathom.api.v2 import fathom_pb2 as _fathom_pb2
from fathom.api.v2 import portfolio_pb2 as _portfolio_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CreateAsyncLargePolygonTaskRequest(_message.Message):
    __slots__ = ("layer_ids", "metadata", "polygon")
    LAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    POLYGON_FIELD_NUMBER: _ClassVar[int]
    layer_ids: _containers.RepeatedScalarFieldContainer[str]
    metadata: _common_pb2.Metadata
    polygon: _fathom_pb2.Polygon
    def __init__(self, layer_ids: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Union[_common_pb2.Metadata, _Mapping]] = ..., polygon: _Optional[_Union[_fathom_pb2.Polygon, _Mapping]] = ...) -> None: ...

class CreateAsyncLargePolygonTaskResponse(_message.Message):
    __slots__ = ("task_id",)
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class CreateAsyncLargeGeoJSONPolygonTaskRequest(_message.Message):
    __slots__ = ("layer_ids", "metadata", "polygon_geojson")
    class PolygonGeojsonEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _struct_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...
    LAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    POLYGON_GEOJSON_FIELD_NUMBER: _ClassVar[int]
    layer_ids: _containers.RepeatedScalarFieldContainer[str]
    metadata: _common_pb2.Metadata
    polygon_geojson: _containers.MessageMap[str, _struct_pb2.Value]
    def __init__(self, layer_ids: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Union[_common_pb2.Metadata, _Mapping]] = ..., polygon_geojson: _Optional[_Mapping[str, _struct_pb2.Value]] = ...) -> None: ...

class CreateAsyncLargeGeoJSONPolygonTaskResponse(_message.Message):
    __slots__ = ("task_id",)
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class CreateAsyncLargeWKTPolygonTaskRequest(_message.Message):
    __slots__ = ("layer_ids", "metadata", "wkt")
    LAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    WKT_FIELD_NUMBER: _ClassVar[int]
    layer_ids: _containers.RepeatedScalarFieldContainer[str]
    metadata: _common_pb2.Metadata
    wkt: str
    def __init__(self, layer_ids: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Union[_common_pb2.Metadata, _Mapping]] = ..., wkt: _Optional[str] = ...) -> None: ...

class CreateAsyncLargeWKTPolygonTaskResponse(_message.Message):
    __slots__ = ("task_id",)
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class GetAsyncTaskStatusRequest(_message.Message):
    __slots__ = ("task_id",)
    TASK_ID_FIELD_NUMBER: _ClassVar[int]
    task_id: str
    def __init__(self, task_id: _Optional[str] = ...) -> None: ...

class GetAsyncTaskStatusResponse(_message.Message):
    __slots__ = ("task_status", "download_url", "errors")
    TASK_STATUS_FIELD_NUMBER: _ClassVar[int]
    DOWNLOAD_URL_FIELD_NUMBER: _ClassVar[int]
    ERRORS_FIELD_NUMBER: _ClassVar[int]
    task_status: _portfolio_pb2.TaskStatus
    download_url: str
    errors: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, task_status: _Optional[_Union[_portfolio_pb2.TaskStatus, str]] = ..., download_url: _Optional[str] = ..., errors: _Optional[_Iterable[str]] = ...) -> None: ...
