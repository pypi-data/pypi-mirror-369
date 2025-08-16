"""Custom exceptions for the Fathom SDK."""


class FathomException(Exception):
    """A client exception."""


class TaskNotCompleteException(FathomException):
    """Tried to download the result from a task that was not complete."""


class InvalidCredentialsError(FathomException):
    """Could not create an authenticated connection to the API."""


class AuthenticationError(FathomException):
    """Could not create an authenticated connection to the API."""


class PortfolioCSVError(FathomException):
    """Error when uploading data for a large portfolio run."""


class GeoJSONError(FathomException):
    """Invalid GeoJSON given."""


class KMLError(FathomException):
    """Invalid KML/KMZ given."""


class VectorFileError(FathomException):
    """Invalid vector file given."""
