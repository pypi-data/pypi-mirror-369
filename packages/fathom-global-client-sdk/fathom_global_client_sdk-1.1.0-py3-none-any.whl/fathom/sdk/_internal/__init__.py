import os
import pathlib

from fathom.sdk._internal.geojson import polygon_from_geojson
from fathom.sdk.exceptions import FathomException


def polygon_from_vector_file(
    vector_file_path: os.PathLike | str,
) -> dict:
    """Load a single polygon from a vector file from the given file path.

    Args:
        vector_file_path: path to vector file

    """
    if not vector_file_path:
        raise Exception("Empty vector file path given")

    vector_file_path = pathlib.PurePath(vector_file_path)
    raw_filename = os.fspath(vector_file_path)

    if raw_filename.endswith(".kmz"):
        from fathom.sdk._internal.kml import polygon_from_kmz

        return polygon_from_kmz(vector_file_path)
    elif raw_filename.endswith(".kml"):
        from fathom.sdk._internal.kml import polygon_from_kml

        return polygon_from_kml(vector_file_path)
    elif raw_filename.endswith(".gpkg"):
        from fathom.sdk._internal.vector_file import polygon_from_geopkg

        return polygon_from_geopkg(vector_file_path)
    elif raw_filename.endswith(".shp"):
        from fathom.sdk._internal.vector_file import polygon_from_shapefile

        return polygon_from_shapefile(vector_file_path)
    elif raw_filename.endswith(".json") or raw_filename.endswith(".geojson"):
        return polygon_from_geojson(vector_file_path)

    raise FathomException(
        f"Not a supported vector file extension: '{vector_file_path}'"
    )
