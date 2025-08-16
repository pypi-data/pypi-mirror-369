from buf.validate import validate_pb2 as _validate_pb2
from fathom.api.v2 import common_pb2 as _common_pb2
from google.api import annotations_pb2 as _annotations_pb2
from google.protobuf import struct_pb2 as _struct_pb2
from protoc_gen_openapiv2.options import annotations_pb2 as _annotations_pb2_1
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Shape(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SHAPE_UNSPECIFIED: _ClassVar[Shape]
    SHAPE_CIRCLE: _ClassVar[Shape]
    SHAPE_SQUARE: _ClassVar[Shape]

class PolygonResultCode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    POLYGON_RESULT_CODE_UNSPECIFIED: _ClassVar[PolygonResultCode]
    POLYGON_RESULT_CODE_OUT_OF_BOUNDS: _ClassVar[PolygonResultCode]
    POLYGON_RESULT_CODE_OK: _ClassVar[PolygonResultCode]

class Resolution(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESOLUTION_UNSPECIFIED: _ClassVar[Resolution]
    RESOLUTION_1_ARC_SEC: _ClassVar[Resolution]
    RESOLUTION_THIRD_ARC_SEC: _ClassVar[Resolution]
    RESOLUTION_3_ARC_SEC: _ClassVar[Resolution]
SHAPE_UNSPECIFIED: Shape
SHAPE_CIRCLE: Shape
SHAPE_SQUARE: Shape
POLYGON_RESULT_CODE_UNSPECIFIED: PolygonResultCode
POLYGON_RESULT_CODE_OUT_OF_BOUNDS: PolygonResultCode
POLYGON_RESULT_CODE_OK: PolygonResultCode
RESOLUTION_UNSPECIFIED: Resolution
RESOLUTION_1_ARC_SEC: Resolution
RESOLUTION_THIRD_ARC_SEC: Resolution
RESOLUTION_3_ARC_SEC: Resolution

class GetPolygonDataRequest(_message.Message):
    __slots__ = ("layer_ids", "metadata", "polygon")
    LAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    POLYGON_FIELD_NUMBER: _ClassVar[int]
    layer_ids: _containers.RepeatedScalarFieldContainer[str]
    metadata: _common_pb2.Metadata
    polygon: Polygon
    def __init__(self, layer_ids: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Union[_common_pb2.Metadata, _Mapping]] = ..., polygon: _Optional[_Union[Polygon, _Mapping]] = ...) -> None: ...

class GetPolygonDataResponse(_message.Message):
    __slots__ = ("results",)
    class ResultsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: PolygonResult
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[PolygonResult, _Mapping]] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.MessageMap[str, PolygonResult]
    def __init__(self, results: _Optional[_Mapping[str, PolygonResult]] = ...) -> None: ...

class GetPointsDataRequest(_message.Message):
    __slots__ = ("layer_ids", "metadata", "points")
    LAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    layer_ids: _containers.RepeatedScalarFieldContainer[str]
    metadata: _common_pb2.Metadata
    points: _containers.RepeatedCompositeFieldContainer[Point]
    def __init__(self, layer_ids: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Union[_common_pb2.Metadata, _Mapping]] = ..., points: _Optional[_Iterable[_Union[Point, _Mapping]]] = ...) -> None: ...

class GetPointsDataResponse(_message.Message):
    __slots__ = ("results",)
    class ResultsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: PointResult
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[PointResult, _Mapping]] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.MessageMap[str, PointResult]
    def __init__(self, results: _Optional[_Mapping[str, PointResult]] = ...) -> None: ...

class QuotePointsRequest(_message.Message):
    __slots__ = ("layer_ids", "points")
    LAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    POINTS_FIELD_NUMBER: _ClassVar[int]
    layer_ids: _containers.RepeatedScalarFieldContainer[str]
    points: _containers.RepeatedCompositeFieldContainer[Point]
    def __init__(self, layer_ids: _Optional[_Iterable[str]] = ..., points: _Optional[_Iterable[_Union[Point, _Mapping]]] = ...) -> None: ...

class QuotePolygonRequest(_message.Message):
    __slots__ = ("layer_ids", "polygon")
    LAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    POLYGON_FIELD_NUMBER: _ClassVar[int]
    layer_ids: _containers.RepeatedScalarFieldContainer[str]
    polygon: Polygon
    def __init__(self, layer_ids: _Optional[_Iterable[str]] = ..., polygon: _Optional[_Union[Polygon, _Mapping]] = ...) -> None: ...

class QuotePointsResponse(_message.Message):
    __slots__ = ("total", "currency")
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    total: float
    currency: str
    def __init__(self, total: _Optional[float] = ..., currency: _Optional[str] = ...) -> None: ...

class QuotePolygonResponse(_message.Message):
    __slots__ = ("total", "currency")
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    CURRENCY_FIELD_NUMBER: _ClassVar[int]
    total: float
    currency: str
    def __init__(self, total: _Optional[float] = ..., currency: _Optional[str] = ...) -> None: ...

class GetGeoJSONPointsDataRequest(_message.Message):
    __slots__ = ("layer_ids", "metadata", "points_geojson")
    class PointsGeojsonEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: _struct_pb2.Value
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[_struct_pb2.Value, _Mapping]] = ...) -> None: ...
    LAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    POINTS_GEOJSON_FIELD_NUMBER: _ClassVar[int]
    layer_ids: _containers.RepeatedScalarFieldContainer[str]
    metadata: _common_pb2.Metadata
    points_geojson: _containers.MessageMap[str, _struct_pb2.Value]
    def __init__(self, layer_ids: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Union[_common_pb2.Metadata, _Mapping]] = ..., points_geojson: _Optional[_Mapping[str, _struct_pb2.Value]] = ...) -> None: ...

class GetGeoJSONPolygonDataRequest(_message.Message):
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

class GetGeoJSONPolygonStatsRequest(_message.Message):
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

class GetPolygonStatsRequest(_message.Message):
    __slots__ = ("layer_ids", "metadata", "polygon")
    LAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    POLYGON_FIELD_NUMBER: _ClassVar[int]
    layer_ids: _containers.RepeatedScalarFieldContainer[str]
    metadata: _common_pb2.Metadata
    polygon: Polygon
    def __init__(self, layer_ids: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Union[_common_pb2.Metadata, _Mapping]] = ..., polygon: _Optional[_Union[Polygon, _Mapping]] = ...) -> None: ...

class GetPolygonStatsResponse(_message.Message):
    __slots__ = ("results",)
    class ResultsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: PolygonStats
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[PolygonStats, _Mapping]] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.MessageMap[str, PolygonStats]
    def __init__(self, results: _Optional[_Mapping[str, PolygonStats]] = ...) -> None: ...

class GetShapePolygonStatsRequest(_message.Message):
    __slots__ = ("layer_ids", "metadata", "shape", "size", "center")
    LAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    SHAPE_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    CENTER_FIELD_NUMBER: _ClassVar[int]
    layer_ids: _containers.RepeatedScalarFieldContainer[str]
    metadata: _common_pb2.Metadata
    shape: Shape
    size: int
    center: Point
    def __init__(self, layer_ids: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Union[_common_pb2.Metadata, _Mapping]] = ..., shape: _Optional[_Union[Shape, str]] = ..., size: _Optional[int] = ..., center: _Optional[_Union[Point, _Mapping]] = ...) -> None: ...

class GetShapePolygonStatsResponse(_message.Message):
    __slots__ = ("results",)
    class ResultsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: PolygonStats
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[PolygonStats, _Mapping]] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.MessageMap[str, PolygonStats]
    def __init__(self, results: _Optional[_Mapping[str, PolygonStats]] = ...) -> None: ...

class GetWKTPolygonStatsRequest(_message.Message):
    __slots__ = ("layer_ids", "metadata", "wkt")
    LAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    WKT_FIELD_NUMBER: _ClassVar[int]
    layer_ids: _containers.RepeatedScalarFieldContainer[str]
    metadata: _common_pb2.Metadata
    wkt: str
    def __init__(self, layer_ids: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Union[_common_pb2.Metadata, _Mapping]] = ..., wkt: _Optional[str] = ...) -> None: ...

class GetWKTPolygonStatsResponse(_message.Message):
    __slots__ = ("results",)
    class ResultsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: PolygonStats
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[PolygonStats, _Mapping]] = ...) -> None: ...
    RESULTS_FIELD_NUMBER: _ClassVar[int]
    results: _containers.MessageMap[str, PolygonStats]
    def __init__(self, results: _Optional[_Mapping[str, PolygonStats]] = ...) -> None: ...

class CreateAccessTokenRequest(_message.Message):
    __slots__ = ("client_id", "client_secret")
    CLIENT_ID_FIELD_NUMBER: _ClassVar[int]
    CLIENT_SECRET_FIELD_NUMBER: _ClassVar[int]
    client_id: str
    client_secret: str
    def __init__(self, client_id: _Optional[str] = ..., client_secret: _Optional[str] = ...) -> None: ...

class CreateAccessTokenResponse(_message.Message):
    __slots__ = ("access_token", "expire_secs")
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    EXPIRE_SECS_FIELD_NUMBER: _ClassVar[int]
    access_token: str
    expire_secs: int
    def __init__(self, access_token: _Optional[str] = ..., expire_secs: _Optional[int] = ...) -> None: ...

class PolygonResult(_message.Message):
    __slots__ = ("geo_tiff", "code")
    GEO_TIFF_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    geo_tiff: bytes
    code: PolygonResultCode
    def __init__(self, geo_tiff: _Optional[bytes] = ..., code: _Optional[_Union[PolygonResultCode, str]] = ...) -> None: ...

class PointResultValue(_message.Message):
    __slots__ = ("query_point", "val")
    QUERY_POINT_FIELD_NUMBER: _ClassVar[int]
    VAL_FIELD_NUMBER: _ClassVar[int]
    query_point: Point
    val: int
    def __init__(self, query_point: _Optional[_Union[Point, _Mapping]] = ..., val: _Optional[int] = ...) -> None: ...

class PointResult(_message.Message):
    __slots__ = ("values",)
    VALUES_FIELD_NUMBER: _ClassVar[int]
    values: _containers.RepeatedCompositeFieldContainer[PointResultValue]
    def __init__(self, values: _Optional[_Iterable[_Union[PointResultValue, _Mapping]]] = ...) -> None: ...

class Point(_message.Message):
    __slots__ = ("longitude", "latitude")
    LONGITUDE_FIELD_NUMBER: _ClassVar[int]
    LATITUDE_FIELD_NUMBER: _ClassVar[int]
    longitude: float
    latitude: float
    def __init__(self, longitude: _Optional[float] = ..., latitude: _Optional[float] = ...) -> None: ...

class Polygon(_message.Message):
    __slots__ = ("points",)
    POINTS_FIELD_NUMBER: _ClassVar[int]
    points: _containers.RepeatedCompositeFieldContainer[Point]
    def __init__(self, points: _Optional[_Iterable[_Union[Point, _Mapping]]] = ...) -> None: ...

class PolygonStats(_message.Message):
    __slots__ = ("mean", "min", "max", "std_dev", "share_above_zero")
    MEAN_FIELD_NUMBER: _ClassVar[int]
    MIN_FIELD_NUMBER: _ClassVar[int]
    MAX_FIELD_NUMBER: _ClassVar[int]
    STD_DEV_FIELD_NUMBER: _ClassVar[int]
    SHARE_ABOVE_ZERO_FIELD_NUMBER: _ClassVar[int]
    mean: int
    min: int
    max: int
    std_dev: int
    share_above_zero: float
    def __init__(self, mean: _Optional[int] = ..., min: _Optional[int] = ..., max: _Optional[int] = ..., std_dev: _Optional[int] = ..., share_above_zero: _Optional[float] = ...) -> None: ...

class GetLargePolygonDataRequest(_message.Message):
    __slots__ = ("layer_ids", "metadata", "polygon")
    LAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    POLYGON_FIELD_NUMBER: _ClassVar[int]
    layer_ids: _containers.RepeatedScalarFieldContainer[str]
    metadata: _common_pb2.Metadata
    polygon: Polygon
    def __init__(self, layer_ids: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Union[_common_pb2.Metadata, _Mapping]] = ..., polygon: _Optional[_Union[Polygon, _Mapping]] = ...) -> None: ...

class GetLargePolygonDataResponse(_message.Message):
    __slots__ = ("download_url", "result_codes")
    class ResultCodesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: PolygonResultCode
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[PolygonResultCode, str]] = ...) -> None: ...
    DOWNLOAD_URL_FIELD_NUMBER: _ClassVar[int]
    RESULT_CODES_FIELD_NUMBER: _ClassVar[int]
    download_url: str
    result_codes: _containers.ScalarMap[str, PolygonResultCode]
    def __init__(self, download_url: _Optional[str] = ..., result_codes: _Optional[_Mapping[str, PolygonResultCode]] = ...) -> None: ...

class GetLargeWKTPolygonDataRequest(_message.Message):
    __slots__ = ("layer_ids", "metadata", "wkt")
    LAYER_IDS_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    WKT_FIELD_NUMBER: _ClassVar[int]
    layer_ids: _containers.RepeatedScalarFieldContainer[str]
    metadata: _common_pb2.Metadata
    wkt: str
    def __init__(self, layer_ids: _Optional[_Iterable[str]] = ..., metadata: _Optional[_Union[_common_pb2.Metadata, _Mapping]] = ..., wkt: _Optional[str] = ...) -> None: ...

class GetLargeWKTPolygonDataResponse(_message.Message):
    __slots__ = ("download_url", "result_codes")
    class ResultCodesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: PolygonResultCode
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[PolygonResultCode, str]] = ...) -> None: ...
    DOWNLOAD_URL_FIELD_NUMBER: _ClassVar[int]
    RESULT_CODES_FIELD_NUMBER: _ClassVar[int]
    download_url: str
    result_codes: _containers.ScalarMap[str, PolygonResultCode]
    def __init__(self, download_url: _Optional[str] = ..., result_codes: _Optional[_Mapping[str, PolygonResultCode]] = ...) -> None: ...

class GetLargeGeoJSONPolygonDataRequest(_message.Message):
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

class GetLargeGeoJSONPolygonDataResponse(_message.Message):
    __slots__ = ("download_url", "result_codes")
    class ResultCodesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: PolygonResultCode
        def __init__(self, key: _Optional[str] = ..., value: _Optional[_Union[PolygonResultCode, str]] = ...) -> None: ...
    DOWNLOAD_URL_FIELD_NUMBER: _ClassVar[int]
    RESULT_CODES_FIELD_NUMBER: _ClassVar[int]
    download_url: str
    result_codes: _containers.ScalarMap[str, PolygonResultCode]
    def __init__(self, download_url: _Optional[str] = ..., result_codes: _Optional[_Mapping[str, PolygonResultCode]] = ...) -> None: ...
