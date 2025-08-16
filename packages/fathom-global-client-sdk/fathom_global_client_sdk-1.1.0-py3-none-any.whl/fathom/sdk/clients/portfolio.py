import dataclasses
import logging
import os
from typing import TYPE_CHECKING

import requests

from fathom.api.v2 import portfolio_pb2, portfolio_pb2_grpc
from fathom.sdk._internal.common import _metadata_from_project_id
from fathom.sdk.common import PathOrString
from fathom.sdk.exceptions import (
    PortfolioCSVError,
    TaskNotCompleteException,
)

if TYPE_CHECKING:
    from fathom.sdk.client import BaseClient


log = logging.getLogger(__name__)


@dataclasses.dataclass
class PortfolioClient:
    """Sub-client for interacting with portfolios.

    Example: Triggering large portfolio requests
        ```python
        import time

        from fathom.api.v2 import portfolio_pb2
        from fathom.sdk.v2 import Client

        client = Client(...)
        layer_ids = [...]

        create_resp = client.portfolio.create_task(layer_ids)

        client.portfolio.upload_portfolio_csv(create_resp.upload_url, "/path/to/input.csv")

        for i in range(100):
            time.sleep(10)

            status = client.portfolio.task_status(create_resp.task_id)
            if status.task_status == portfolio_pb2.TASK_STATUS_COMPLETE:
                break
            elif status.task_status == portfolio_pb2.TASK_STATUS_ERROR:
                raise Exception(f"task failed: {status}")
        else:
            raise Exception("task was not ready in time")

        num_bytes_read = client.portfolio.attempt_task_result_download(
            create_resp.task_id, "/path/to/output.csv"
        )
        ```
    """

    base_client: "BaseClient"

    def _service_stub(self) -> portfolio_pb2_grpc.PortfolioServiceStub:
        """Return the gRPC service stub."""
        return self.base_client._get_stub(portfolio_pb2_grpc.PortfolioServiceStub)

    def create_task(
        self,
        layer_ids: list[str],
        project_id: str | None = None,
    ) -> portfolio_pb2.CreatePortfolioTaskResponse:
        """Create a new portfolio task.

        Args:
            layer_ids: Layer IDs to use for task
            project_id: Identifier to differentiate projects using the API.

        Returns:
            A CreatePortfolioTaskResponse object containing the task details.

        """
        metadata = _metadata_from_project_id(project_id)
        request = portfolio_pb2.CreatePortfolioTaskRequest(
            layer_ids=layer_ids, metadata=metadata
        )

        log.debug("Creating new portfolio task")

        return self._service_stub().CreatePortfolioTask(request)

    def task_status(self, task_id: str) -> portfolio_pb2.GetPortfolioTaskStatusResponse:
        """Get the status of an existing portfolio task.

        Args:
            task_id: ID of previously created portfolio task

        Returns:
            A GetPortfolioTaskStatusResponse object containing the task status.

        """
        request = portfolio_pb2.GetPortfolioTaskStatusRequest(
            task_id=task_id,
        )

        log.debug(f"Getting status of task '{task_id}")

        return self._service_stub().GetPortfolioTaskStatus(request)

    def attempt_task_result_download(
        self, task_id: str, output_path: PathOrString, chunk_size: int = 1000
    ) -> int:
        """Attempt to download the result of a given task.

        Should only be called after a call to
        `task_status` has indicated that the task completed without errors, otherwise an
        exception will be raised.

        Args:
            task_id: ID of previously created portfolio task
            output_path: Name of file to download output in to. It will be OVERWRITTEN if it already exists.
            chunk_size: Override chunk size when downloading CSV

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

        log.debug(f"Downloading results of portfolio task to {output_path}")

        bytes_read = 0

        # stream response to avoid having to download hundreds of MB into memory first
        with open(output_path, "wb") as output_file:
            streaming_resp = requests.api.get(task_status.download_url, stream=True)

            for chunk in streaming_resp.iter_content(chunk_size):
                output_file.write(chunk)
                bytes_read += len(chunk)

        return bytes_read

    @staticmethod
    def upload_portfolio_csv(
        upload_url: str, input_path: PathOrString, *, timeout: int = 10
    ):
        """Upload the given portfolio CSV file for the portfolio task.

        Args:
            upload_url: upload url from a previous CreatePortfolioTaskResponse
            input_path: path to CSV file to upload
            timeout: timeout on uploading CSV

        """
        log.debug(f"Uploading portfolio input from {input_path}")

        with open(input_path, "rb") as csv_file:
            size = os.path.getsize(input_path)
            extra_headers = {
                "content-length": str(size),
                "content-type": "text/csv",
                "x-goog-content-length-range": "0,524288000",
            }
            resp = requests.api.put(
                url=upload_url,
                data=csv_file,
                headers=extra_headers,
                timeout=timeout,
            )

        if resp.status_code != 200:
            raise PortfolioCSVError(f"Error uploading CSV: {resp}")

    def cancel_task(self, task_id: str) -> None:
        """Cancel a portfolio task.

        Args:
            task_id: ID of previously created portfolio task

        """
        request = portfolio_pb2.CancelPortfolioTaskRequest(
            task_id=task_id,
        )

        log.debug(f"Cancelling task '{task_id}'")

        self._service_stub().CancelPortfolioTask(request)
