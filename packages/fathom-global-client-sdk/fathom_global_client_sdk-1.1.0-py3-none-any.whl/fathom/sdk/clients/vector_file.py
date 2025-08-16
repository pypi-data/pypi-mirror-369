import dataclasses
import os
from typing import TYPE_CHECKING

from fathom.api.v2 import fathom_pb2, fathom_pb2_grpc
from fathom.sdk._internal import polygon_from_vector_file
from fathom.sdk.common import check_polygon_order

if TYPE_CHECKING:
    from fathom.sdk.v2 import Client


@dataclasses.dataclass
class VectorFileClient:
    r"""Sub-client for fetching data using polygons encoded in vector files.

    Supported vector types:

    - KML and KMZ files
    - GeoJSON
    - Shapefiles
    - GeoPackage

    Each file must contain exactly one polygon 'feature' which follows the rules
    for other [polygon queries](../usage.md#polygon-queries).

    Additionally, GeoJSON files must follow the same rules as defined in
    the [GeoJSON query documentation](../usage.md#geojson-queries).

    Example: Vector file queries
        ```python
        from fathom.sdk.v2 import Client

        client = Client(...)
        layer_ids = [...]

        polygon_resp = client.vector_file_name.get_polygon_stats("/path/to/file.kml", layer_ids)
        # On Windows, use the 'r' prefix to the path:
        # polygon_resp = client.vector_file_name.get_polygon_stats(r"C:\\Users\\MyUser\\file.kml", layer_ids)
        ```
    """

    client: "Client"

    def _service_stub(self) -> fathom_pb2_grpc.FathomServiceStub:
        """Return the gRPC service stub."""
        return self.client._get_stub(fathom_pb2_grpc.FathomServiceStub)

    def get_polygon(
        self,
        vector_file_name: str | os.PathLike,
        layer_ids: list[str],
        project_id: str | None = None,
        *,
        correct_polygon_points_order: bool = False,
    ) -> fathom_pb2.GetPolygonDataResponse:
        """Return data pertaining to a polygon contained in the given vector file.

        Args:
            vector_file_name: path to a vector file in one of the supported formats
            layer_ids: Layer IDs to use for task
            project_id: Identifier to differentiate projects using the API.
            correct_polygon_points_order:
                If set to True, attempt to correct the order of polygon points. If the polygon contained in the given vector
                file has points in the incorrect order (counter-clockwise) this will be rejected by the API, Enabling this
                option reverses the points before sending it to the API.

        Returns:
            A GetPolygonDataResponse object containing the data for the polygon.

        """
        geojson = polygon_from_vector_file(vector_file_name)
        check_polygon_order(geojson, correct_polygon_points_order)

        return self.client.geojson.get_polygon(
            geojson,
            layer_ids=layer_ids,
            project_id=project_id,
        )

    def get_large_polygon(
        self,
        vector_file_name: str | os.PathLike,
        layer_ids: list[str],
        project_id: str | None = None,
        *,
        correct_polygon_points_order: bool = False,
    ) -> fathom_pb2.GetLargePolygonDataResponse:
        """Return data pertaining to a large polygon contained in the given vector file.

        Args:
            vector_file_name: path to a vector file in one of the supported formats
            layer_ids: Layer IDs to use for task
            project_id: Identifier to differentiate projects using the API.
            correct_polygon_points_order:
                If set to True, attempt to correct the order of polygon points. If the polygon contained in the given vector
                file has points in the incorrect order (counter-clockwise) this will be rejected by the API, Enabling this
                option reverses the points before sending it to the API.

        Returns:
            A GetLargePolygonDataResponse object containing the data for the large polygon.

        """
        geojson = polygon_from_vector_file(vector_file_name)
        check_polygon_order(geojson, correct_polygon_points_order)

        return self.client.geojson.get_large_polygon(
            geojson,
            layer_ids=layer_ids,
            project_id=project_id,
        )

    def get_polygon_stats(
        self,
        vector_file_name: str | os.PathLike,
        layer_ids: list[str],
        project_id: str | None = None,
        *,
        correct_polygon_points_order: bool = False,
    ) -> fathom_pb2.GetPolygonStatsResponse:
        """Return stats pertaining to a polygon contained in the given vector file.

        Args:
            vector_file_name: path to a vector file in one of the supported formats
            layer_ids: Layer IDs to use for task
            project_id: Identifier to differentiate projects using the API.
            correct_polygon_points_order:
                If set to True, attempt to correct the order of polygon points. If the polygon contained in the given vector
                file has points in the incorrect order (counter-clockwise) this will be rejected by the API, Enabling this
                option reverses the points before sending it to the API.

        Returns:
            A GetPolygonStatsResponse object containing the statistics for the polygon.

        """
        geojson = polygon_from_vector_file(vector_file_name)
        check_polygon_order(geojson, correct_polygon_points_order)

        return self.client.geojson.get_polygon_stats(
            geojson,
            layer_ids=layer_ids,
            project_id=project_id,
        )
