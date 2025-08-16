from fathom.api.v2 import common_pb2


def _metadata_from_project_id(
    project_id: str | None,
) -> common_pb2.Metadata | None:
    """Create metadata from a project ID."""
    return common_pb2.Metadata(project_id=project_id) if project_id else None
