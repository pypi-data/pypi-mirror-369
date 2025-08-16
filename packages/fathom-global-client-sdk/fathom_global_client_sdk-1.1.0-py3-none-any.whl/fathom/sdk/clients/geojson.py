import dataclasses
import io
import os
from typing import TYPE_CHECKING

from google.protobuf import struct_pb2

from fathom.api.v2 import fathom_pb2, fathom_pb2_grpc
from fathom.sdk._internal.common import _metadata_from_project_id
from fathom.sdk._internal.geojson import load_geojson

if TYPE_CHECKING:
    from fathom.sdk.client import BaseClient


@dataclasses.dataclass
class GeoJSONClient:
    """A client to fetch data from the fathom SDK using [GeoJSON](https://geojson.org/).

    The `geojson` input to the method parameters should be one of:

    - An opened file object
    - A string or bytes containing raw GeoJSON
    - A [PathLike](https://docs.python.org/3/library/os.html#os.PathLike) object with the filepath to a geojson file
    - A Python dictionary containing the GeoJSON

    Example: GeoJSON queries
        ```python
        from fathom.sdk.v2 import Client

        client = Client(...)
        layer_ids = [...]

        # With an opened file
        with open("/path/to/geo.json") as geojson_file:
            polygon_resp = client.geojson.get_polygon_stats(geojson_file, layer_ids)

        # With a geojson string
        geojson_string = '{"type": ...}'
        polygon_resp = client.geojson.get_polygon(geojson_string, layer_ids)

        # With a Python dictionary
        polygon_geojson = {
            ...
        }
        polygon_resp = client.geojson.get_polygon(polygon_geojson, layer_ids)
        ```
    """

    base_client: "BaseClient"

    def _service_stub(self) -> fathom_pb2_grpc.FathomServiceStub:
        """Return the gRPC service stub."""
        return self.base_client._get_stub(fathom_pb2_grpc.FathomServiceStub)

    def get_polygon(
        self,
        geojson: os.PathLike
        | str
        | bytes
        | bytearray
        | io.BufferedIOBase
        | io.TextIOBase
        | dict,
        layer_ids: list[str],
        project_id: str | None = None,
    ) -> fathom_pb2.GetPolygonDataResponse:
        """Return data pertaining to a polygon encoded in GeoJSON.

        Args:
            geojson: The GeoJSON data representing the polygon.
                - An opened file object
                - A string or bytes containing raw GeoJSON
                - A PathLike object with the filepath to a GeoJSON file
                - A Python dictionary containing the GeoJSON
            layer_ids: The identifiers of the types of data being requested.
            project_id: Identifier to differentiate projects using the API.

        Returns:
            A GetPolygonDataResponse object containing the data for the polygon.

        """
        loaded_geojson = load_geojson(geojson)

        buffer = struct_pb2.Struct()
        buffer.update(loaded_geojson)

        request = fathom_pb2.GetGeoJSONPolygonDataRequest(
            polygon_geojson=buffer.fields,
            layer_ids=layer_ids,
            metadata=_metadata_from_project_id(project_id),
        )

        return self._service_stub().GetGeoJSONPolygonData(request)

    def get_large_polygon(
        self,
        geojson: os.PathLike
        | str
        | bytes
        | bytearray
        | io.BufferedIOBase
        | io.TextIOBase
        | dict,
        layer_ids: list[str],
        project_id: str | None = None,
    ) -> fathom_pb2.GetLargePolygonDataResponse:
        """Return data pertaining to a large polygon encoded in GeoJSON.

        Args:
            geojson: The GeoJSON data representing the polygon.
                - An opened file object
                - A string or bytes containing raw GeoJSON
                - A PathLike object with the filepath to a GeoJSON file
                - A Python dictionary containing the GeoJSON
            layer_ids: Layer IDs to use for task
            project_id: Identifier to differentiate projects using the API.

        Returns:
            A GetLargePolygonDataResponse object containing the data for the large polygon.

        """
        loaded_geojson = load_geojson(geojson)

        buffer = struct_pb2.Struct()
        buffer.update(loaded_geojson)

        request = fathom_pb2.GetLargeGeoJSONPolygonDataRequest(
            polygon_geojson=buffer.fields,
            layer_ids=layer_ids,
            metadata=_metadata_from_project_id(project_id),
        )

        return self._service_stub().GetLargeGeoJSONPolygonData(request)

    def get_polygon_stats(
        self,
        geojson: os.PathLike
        | str
        | bytes
        | bytearray
        | io.BufferedIOBase
        | io.TextIOBase
        | dict,
        layer_ids: list[str],
        project_id: str | None = None,
    ) -> fathom_pb2.GetPolygonStatsResponse:
        """Return statistics about a polygon encoded in GeoJSON.

        Args:
            geojson: The GeoJSON data representing the polygon.
                - An opened file object
                - A string or bytes containing raw GeoJSON
                - A PathLike object with the filepath to a GeoJSON file
                - A Python dictionary containing the GeoJSON
            layer_ids: The identifiers of the types of data being requested.
            project_id: Identifier to differentiate projects using the API.

        Returns:
            A GetPolygonStatsResponse object containing the statistics for the polygon.

        """
        loaded_geojson = load_geojson(geojson)

        buffer = struct_pb2.Struct()
        buffer.update(loaded_geojson)

        request = fathom_pb2.GetGeoJSONPolygonStatsRequest(
            polygon_geojson=buffer.fields,
            layer_ids=layer_ids,
            metadata=_metadata_from_project_id(project_id),
        )

        return self._service_stub().GetGeoJSONPolygonStats(request)

    def get_points(
        self,
        geojson: os.PathLike
        | str
        | bytes
        | bytearray
        | io.BufferedIOBase
        | io.TextIOBase
        | dict,
        layer_ids: list[str],
        project_id: str | None = None,
    ) -> fathom_pb2.GetPointsDataResponse:
        """Return data pertaining to points encoded in GeoJSON.

        Args:
            geojson: The GeoJSON data representing the points.
                - An opened file object
                - A string or bytes containing raw GeoJSON
                - A PathLike object with the filepath to a GeoJSON file
                - A Python dictionary containing the GeoJSON
            layer_ids: The identifiers of the types of data being requested.
            project_id: Identifier to differentiate projects using the API.

        Returns:
            A GetPointsDataResponse object containing the data for the points.

        """
        loaded_geojson = load_geojson(geojson)

        buffer = struct_pb2.Struct()
        buffer.update(loaded_geojson)

        request = fathom_pb2.GetGeoJSONPointsDataRequest(
            points_geojson=buffer.fields,
            layer_ids=layer_ids,
            metadata=_metadata_from_project_id(project_id),
        )

        return self._service_stub().GetGeoJSONPointsData(request)
