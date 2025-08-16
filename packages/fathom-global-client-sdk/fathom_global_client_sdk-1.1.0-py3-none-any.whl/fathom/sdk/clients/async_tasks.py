import io
import logging
import os
import typing

from google.protobuf import struct_pb2

from fathom.sdk._internal.geojson import load_geojson

if typing.TYPE_CHECKING:
    from fathom.sdk.client import BaseClient
import dataclasses

from fathom.api.v2 import async_pb2, async_pb2_grpc, fathom_pb2, portfolio_pb2
from fathom.sdk._internal.common import _metadata_from_project_id
from fathom.sdk.common import PathOrString, download_file
from fathom.sdk.exceptions import TaskNotCompleteException

log = logging.getLogger(__name__)


@dataclasses.dataclass
class _AsyncBase:
    base_client: "BaseClient"

    def _service_stub(self) -> async_pb2_grpc.AsyncServiceStub:
        """Return the gRPC service stub."""
        return self.base_client._get_stub(async_pb2_grpc.AsyncServiceStub)


class _Geo(_AsyncBase):
    def create_large_polygon_task(
        self,
        polygon: fathom_pb2.Polygon,
        layer_ids: list[str],
        project_id: str | None = None,
    ) -> async_pb2.CreateAsyncLargePolygonTaskResponse:
        """Create a new large polygon task.

        Args:
            polygon: The polygon for which to request data.
            layer_ids: Layer IDs to be requested.
            project_id: Identifier to differentiate projects using the API.

        Returns:
            A CreateAsyncLargePolygonTaskResponse object containing the task ID.

        """
        metadata = _metadata_from_project_id(project_id)
        request = async_pb2.CreateAsyncLargePolygonTaskRequest(
            polygon=polygon,
            layer_ids=layer_ids,
            metadata=metadata,
        )

        log.debug("Creating new async large polygon task")

        return self._service_stub().CreateAsyncLargePolygonTask(request)


class _GeoJson(_AsyncBase):
    def create_large_polygon_task(
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
    ) -> async_pb2.CreateAsyncLargeGeoJSONPolygonTaskResponse:
        """Create a new large polygon task.

        Args:
            geojson: The GeoJSON data representing the polygon.
                - An opened file object
                - A string or bytes containing raw GeoJSON
                - A PathLike object with the filepath to a GeoJSON file
                - A Python dictionary containing the GeoJSON
            layer_ids: Layer IDs to be requested.
            project_id: Identifier to differentiate projects using the API.

        Returns:
            A CreateAsyncLargePolygonTaskResponse object containing the task ID.

        """
        loaded_geojson = load_geojson(geojson)

        buffer = struct_pb2.Struct()
        buffer.update(loaded_geojson)

        metadata = _metadata_from_project_id(project_id)
        request = async_pb2.CreateAsyncLargeGeoJSONPolygonTaskRequest(
            polygon_geojson=buffer.fields,
            layer_ids=layer_ids,
            metadata=metadata,
        )

        log.debug("Creating new async large polygon task")

        return self._service_stub().CreateAsyncLargeGeoJSONPolygonTask(request)


@dataclasses.dataclass
class AsyncTaskClient(_AsyncBase):
    """Sub-client for interacting with asynchronous tasks.

    Usage is roughly the same as [PortfolioClient](./python.md#fathom.sdk.v2.PortfolioClient).
    The task statuses are the same as portfolio statuses.

    !!!note

        The download URL will point to a zip file with the results, see the [async tasks documentation](../../async_tasks.md) for more information.

    Example: Triggering an asynchronous large polygon request
        ```python
        import time

        from fathom.api.v2 import portfolio_pb2
        from fathom.sdk.v2 import Client

        client = Client(...)
        layer_ids = [...]

        # Define a polygon.
        poly = polygon([
            point(51.50, -0.12),
            point(54.51, -0.12),
            point(54.51, -2.11),
            point(51.50, -2.11),
            point(51.50, -0.12),
        ])

        create_resp = client.async_tasks.create_large_polygon_task(poly, layer_ids)

        for i in range(100):
            time.sleep(5)

            status = client.async_tasks.task_status(create_resp.task_id)
            if status.task_status == portfolio_pb2.TASK_STATUS_COMPLETE:
                break
            elif status.task_status == portfolio_pb2.TASK_STATUS_ERROR:
                raise Exception(f"task failed: {status}")
        else:
            raise Exception("task was not ready in time")

        num_bytes_read = client.async_tasks.attempt_task_result_download(
            create_resp.task_id, "/path/to/output.zip"
        )
        ```
    """

    def __post_init__(self):
        self.geo = _Geo(base_client=self.base_client)
        self.geojson = _GeoJson(base_client=self.base_client)

    def task_status(
        self,
        task_id: str,
    ) -> async_pb2.GetAsyncTaskStatusResponse:
        """Get the status of an existing asynchronous task.

        Args:
            task_id: ID of previously created asynchronous task.

        Returns:
            A GetAsyncTaskStatusResponse object containing the task status.

        """
        request = async_pb2.GetAsyncTaskStatusRequest(
            task_id=task_id,
        )

        log.debug(f"Getting status of async task '{task_id}'")

        return self._service_stub().GetAsyncTaskStatus(request)

    def attempt_task_result_download(
        self, task_id: str, output_path: PathOrString, chunk_size: int = 1000
    ) -> int:
        """Attempt to download the result of a given task.

        Should only be called after a call to
        `task_status` has indicated that the task completed without errors, otherwise an
        exception will be raised.

        Args:
            task_id: ID of previously created asynchronous task
            output_path: Name of file to download output in to. It will be OVERWRITTEN if it already exists.
            chunk_size: Override chunk size when downloading file

        Returns:
            Number of bytes downloaded

        Raises:
            TaskNotCompleteException: Task was not ready or there were errors during processing

        """
        task_status = self.task_status(task_id)
        if not task_status.task_status == portfolio_pb2.TASK_STATUS_COMPLETE:
            raise TaskNotCompleteException(
                f"Expected task {task_id} to be COMPLETE, but was {task_status.task_status}"
            )

        log.debug(f"Downloading results of async task to {output_path}")

        return download_file(
            task_status.download_url,
            output_path=output_path,
            chunk_size=chunk_size,
        )
