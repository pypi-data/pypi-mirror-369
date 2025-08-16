"""Functions for interacting with the V2 Fathom API."""

import logging
import warnings

import grpc

from fathom.api.v2 import fathom_pb2

from .client import FATHOM_GRPC_CHANNEL_MSG_SIZE, BaseClient
from .clients.async_tasks import AsyncTaskClient
from .clients.geo import GeoClient
from .clients.geojson import GeoJSONClient
from .clients.portfolio import PortfolioClient
from .clients.vector_file import VectorFileClient
from .common import (
    PathOrString,
    write_tiff_data_to_file,
)

log = logging.getLogger(__name__)


class Client(BaseClient):
    """Fathom SDK v2 client."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        api_address: str = "api.fathom.global",
        msg_channel_size: int = FATHOM_GRPC_CHANNEL_MSG_SIZE,
        *,
        grpc_interceptors: list[grpc.UnaryUnaryClientInterceptor] | None = None,
    ):
        """Construct a new Client, connected to a remote server.

        Args:
            client_id: Client ID to identify a registered client on the
                    authorization server.
            client_secret: Client Secret used with client_id to get an
                    access token.
            api_address: Address of the Fathom API server.
            msg_channel_size: gRPC message channel size, it is 10MB by
                default but if you will be dealing with data size larger than
                the default, you can configure the size.
            grpc_interceptors: An optional list of grpc interceptors to add
                to the grpc channel, for logging or other purposes.

        Attributes:
            geo (GeoClient): Client to talk to the geospatial data API
            geojson (GeoJSONClient): Client to talk to the geospatial data API using GeoJSON
            vector_file_name (VectorFileClient): Client to talk to the geospatial data API using vector file formats
            portfolio (PortfolioClient): Client to talk to the large portfolio API

        """
        super().__init__(
            client_id,
            client_secret,
            api_address,
            msg_channel_size,
            grpc_interceptors=grpc_interceptors,
        )

        self.geo: GeoClient = GeoClient(self)
        self.geojson: GeoJSONClient = GeoJSONClient(self)
        self.portfolio: PortfolioClient = PortfolioClient(self)
        self.vector_file_name: VectorFileClient = VectorFileClient(self)
        self.async_tasks: AsyncTaskClient = AsyncTaskClient(self)


def point(lat: float, lng: float) -> fathom_pb2.Point:
    """Return a Point object for use with Client.get_point().

    Args:
        lat: The latitude of the point.
        lng: The longitude of the point.

    Returns:
        A Point object.

    """
    return fathom_pb2.Point(
        latitude=lat,
        longitude=lng,
    )


def polygon(points: list[fathom_pb2.Point]) -> fathom_pb2.Polygon:
    """Return a Polygon object for use with Client.get_polygon().

    Args:
        points: A list of Point objects defining the polygon boundary.

    Returns:
        A Polygon object.

    """
    return fathom_pb2.Polygon(points=points)


def write_tiffs(
    response: fathom_pb2.GetPolygonDataResponse,
    output_dir: PathOrString,
    *,
    pattern: str = "{layer_id}.tif",
):
    """Write polygon tiff data from a response to the output directory.

    If any polygon result in the response was fully 'no data' (see [key values documentation](../usage.md#key-values)),
    the output tiff will not be written.

    Args:
        response: A response from a `get_polygon` request
        output_dir: the directory to write the tiff data to
        pattern: The pattern to save the file as. Formatted using normal Python string formatting,
            with the only available key being :
                - 'layer_id': the layer id
                - 'sep': The os-specific directory separator

    """
    polygon: fathom_pb2.PolygonResult
    for layer_id, polygon in response.results.items():
        if polygon.code == fathom_pb2.POLYGON_RESULT_CODE_OUT_OF_BOUNDS:
            warnings.warn(
                f"polygon result for layer {layer_id} was all 'no data' - no output file will be written for this "
                "result. In future, this will raise an exception.",
                FutureWarning,
                stacklevel=2,
            )
            continue

        write_tiff_data_to_file(polygon.geo_tiff, layer_id, output_dir, pattern, 0)
