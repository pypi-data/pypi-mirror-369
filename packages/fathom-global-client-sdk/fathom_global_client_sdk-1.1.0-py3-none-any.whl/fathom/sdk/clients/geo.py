import dataclasses
from typing import TYPE_CHECKING

from fathom.api.v2 import fathom_pb2, fathom_pb2_grpc
from fathom.sdk._internal.common import _metadata_from_project_id

if TYPE_CHECKING:
    from fathom.sdk.client import BaseClient


@dataclasses.dataclass
class GeoClient:
    """A sub-client for synchronously fetching data for points or polygons."""

    base_client: "BaseClient"

    def _service_stub(self) -> fathom_pb2_grpc.FathomServiceStub:
        """Return the gRPC service stub."""
        return self.base_client._get_stub(fathom_pb2_grpc.FathomServiceStub)

    def get_points(
        self,
        points: list[fathom_pb2.Point],
        layer_ids: list[str],
        project_id: str | None = None,
    ) -> fathom_pb2.GetPointsDataResponse:
        """Return data pertaining to a list of lat-lng coordinates.

        Args:
            points: A list of coordinates.
            layer_ids: The identifiers of the types of data being requested.
            project_id: Identifier to differentiate projects using the API.

        Returns:
            A GetPointsDataResponse object containing the data for the points.

        """
        request = fathom_pb2.GetPointsDataRequest(
            points=points,
            layer_ids=layer_ids,
            metadata=_metadata_from_project_id(project_id),
        )

        return self._service_stub().GetPointsData(request)

    def get_polygon(
        self,
        polygon: fathom_pb2.Polygon,
        layer_ids: list[str],
        project_id: str | None = None,
    ) -> fathom_pb2.GetPolygonDataResponse:
        """Return data pertaining to a polygon coordinates.

        Args:
            polygon: The bounding points of an area for which data are requested.
                The first and last point MUST be the same, and the loop MUST be in a
                counterclockwise direction (i.e. on the left-hand side of an observer
                walking along the boundary).
            layer_ids: The identifiers of the types of data being requested.
            project_id: Identifier to differentiate projects using the API.

        Returns:
            A GetPolygonDataResponse object containing the data for the polygon.

        """
        request = fathom_pb2.GetPolygonDataRequest(
            polygon=polygon,
            layer_ids=layer_ids,
            metadata=_metadata_from_project_id(project_id),
        )

        return self._service_stub().GetPolygonData(request)

    def get_large_polygon(
        self,
        polygon: fathom_pb2.Polygon,
        layer_ids: list[str],
        project_id: str | None = None,
    ) -> fathom_pb2.GetLargePolygonDataResponse:
        """Return data pertaining to a large polygon coordinates.

        Args:
            polygon: The bounding points of an area for which data are requested.
                The first and last point MUST be the same, and the loop MUST be in a
                counterclockwise direction (i.e. on the left-hand side of an observer
                walking along the boundary).
            layer_ids: The identifiers of the types of data being requested.
            project_id: Identifier to differentiate projects using the API.

        Returns:
            A GetLargePolygonDataResponse object containing the data for the large polygon.

        Example: Fetching large polygon data
            ```python
            import requests

            from fathom.api.v2 import fathom_pb2
            from fathom.sdk.v2 import Client, point, polygon

            client = Client(...)
            layer_ids = [...]

            # Define a polygon
            poly = polygon([
                point(51.50, -0.12),
                point(51.51, -0.12),
                point(51.51, -0.11),
                point(51.50, -0.11),
                point(51.50, -0.12),
            ])

            # Request the large polygon data
            large_poly_resp = client.geo.get_large_polygon(poly, layer_ids)

            # Print the result codes for each layer
            print("Result codes per layer:")
            for layer_id, result_code in large_poly_resp.result_codes.items():
                # Map the integer result code to its string name
                result_code_name = fathom_pb2.PolygonResultCode.Name(result_code)
                print(f"  {layer_id}: {result_code_name}")

            # Download the data using the provided URL
            download_url = large_poly_resp.download_url
            print(f"Downloading data from: {download_url}")

            response = requests.get(download_url)
            response.raise_for_status() # Raise an exception for bad status codes

            # Process the downloaded data (e.g., save to a file)
            with open("large_polygon_data.zip", "wb") as f:
                f.write(response.content)
            ```

        """
        request = fathom_pb2.GetLargePolygonDataRequest(
            polygon=polygon,
            layer_ids=layer_ids,
            metadata=_metadata_from_project_id(project_id),
        )

        return self._service_stub().GetLargePolygonData(request)

    def get_polygon_stats(
        self,
        polygon: fathom_pb2.Polygon,
        layer_ids: list[str],
        project_id: str | None = None,
    ) -> fathom_pb2.GetPolygonStatsResponse:
        """Return statistics about polygons using the given layer_ids.

        This is similar to the get_polygons method, but will only return statistics about the polygon,
        not the polygon itself. To see what statistics are returned, see [the gRPC documentation](
        ../compile_proto_docs.md#polygonstats)

        Args:
            polygon: The bounding points of an area for which data are requested.
                The first and last point MUST be the same, and the loop MUST be in a
                counterclockwise direction (i.e. on the left-hand side of an observer
                walking along the boundary).
            layer_ids: The identifiers of the types of data being requested.
            project_id: Identifier to differentiate projects using the API.

        Returns:
            A GetPolygonStatsResponse object containing the statistics for the polygon.

        """
        request = fathom_pb2.GetPolygonStatsRequest(
            polygon=polygon,
            layer_ids=layer_ids,
            metadata=_metadata_from_project_id(project_id),
        )

        return self._service_stub().GetPolygonStats(request)

    def quote_polygon(
        self,
        polygon: fathom_pb2.Polygon,
        layer_ids: list[str],
    ) -> fathom_pb2.QuotePolygonResponse:
        """Quote the cost to get polygon data.

        Args:
            polygon: The bounding points of an area for which data are requested.
                The first and last point MUST be the same, and the loop MUST be in a
                counterclockwise direction (i.e. on the left-hand side of an observer
                walking along the boundary).
            layer_ids: The identifiers of the types of data being requested.

        Returns:
            A QuotePolygonResponse object containing the quote for the polygon data.

        """
        request = fathom_pb2.QuotePolygonRequest(
            polygon=polygon,
            layer_ids=layer_ids,
        )

        return self._service_stub().QuotePolygon(request)

    def quote_points(
        self,
        points: list[fathom_pb2.Point],
        layer_ids: list[str],
    ) -> fathom_pb2.QuotePointsResponse:
        """Quote the cost to get points data.

        Args:
            points: A list of coordinates.
            layer_ids: The identifiers of the types of data being requested.

        Returns:
            A QuotePointsResponse object containing the quote for the points data.

        """
        request = fathom_pb2.QuotePointsRequest(
            points=points,
            layer_ids=layer_ids,
        )

        return self._service_stub().QuotePoints(request)
