"""Common utility functions for the Fathom SDK."""

import logging
import os

import requests

from .exceptions import GeoJSONError

PathOrString = os.PathLike | str


def write_tiff_data_to_file(
    geotiff_bytes: bytes,
    layer_id: str,
    output_dir: PathOrString,
    pattern: str,
    tiff_num: int,
) -> None:
    """Write GeoTIFF data to a file based on the provided pattern and parameters.

    Args:
        geotiff_bytes: The byte data of the GeoTIFF to be written.
        layer_id: The identifier for the layer.
        output_dir: The directory where the file will be saved.
        pattern: The filename pattern to use, which can include placeholders for `sep`, `layer_id`, and `tiff_num`.
        tiff_num: The number of the TIFF file, used in the filename pattern.

    Raises:
        OSError: If there is an issue creating the directory or writing the file.

    """
    format_vars = {
        "sep": os.sep,
        "layer_id": layer_id,
        "tiff_num": tiff_num,
    }
    base = pattern.format(**format_vars)
    filename = os.path.join(output_dir, base)
    tiff_dir = os.path.dirname(filename)
    os.makedirs(tiff_dir, exist_ok=True)
    with open(filename, "wb") as shapefile:
        shapefile.write(geotiff_bytes)


def check_polygon_order(
    geojson: dict,
    correct_polygon_points_order: bool = False,
):
    """Check if the polygon contained in the geojson is in the right order.

    This function can only check the polygon order if there is exactly one Polygon at the top level of the GeoJSON.
    Some errors (e.g. nested polygons, invalid GeoJSON structure) may not be caught by this function and will only be detected by the server.
    If correct_polygon_points_order is True and the points in the given polygon are in the wrong order (clockwise instead of counter-clockwise),
    this function reverses the points in the GeoJSON in-place. If correct_polygon_points_order is False, it logs a warning instead.

    Args:
        geojson: The loaded GeoJSON
        correct_polygon_points_order: if True, and the points in the given
            polygon are in the wrong order (clockwise instead of counter-clockwise),
            reverse the points in the GeoJSON _in place_. If False, log a warning
            and continue.

    Raises:
        GeoJSONError: If the GeoJSON is missing a geometry type.

    Note:
        This function modifies the input GeoJSON in-place.

    Example:
        ```python
        import json
        from fathom.sdk.common import check_polygon_order

        poly = json.loads('{"type": "Polygon", "coordinates": [[[100.0, 0.0], [101.0, 0.0], [101.0, 1.0], [100.0, 1.0], [100.0, 0.0]]]}')
        check_polygon_order(poly)
        ```

    """
    geom_type = geojson.get("type", None)

    if not geom_type:
        raise GeoJSONError("No geometry type in GeoJSON")

    if geom_type != "Polygon":
        # This might be a 'Feature' or 'FeatureCollection' or something - if so,
        # defer checking to the API which has all the complicated parsing
        logging.debug("Deferring checking non-polygon type")
        return

    coordinates = geojson.get("coordinates", None)
    if (
        not coordinates
        or not isinstance(coordinates, list)
        or len(coordinates) != 1
        or not isinstance(coordinates[0], list)
    ):
        # This might be a nested polygon
        logging.debug("deferring checking zero coordinate type")
        return

    angle = 0.0
    ring = coordinates[0]
    for i, _ in enumerate(ring):
        j = (i + len(ring) - 1) % len(ring)
        res = (ring[i][0] - ring[j][0]) * (ring[i][1] + ring[j][1])
        angle += res

    if angle > 0:
        if correct_polygon_points_order:
            geojson["coordinates"][0] = coordinates[0][::-1]
        else:
            logging.warning(
                "Polygon ring must be in counter-clockwise order - this will be rejected by the API"
            )


def download_file(download_url: str, output_path: PathOrString, chunk_size: int) -> int:
    """Download a file from a URL to a local path."""
    bytes_read = 0

    # stream response to avoid having to download large files into memory first
    with open(output_path, "wb") as output_file:
        streaming_resp = requests.api.get(download_url, stream=True)
        streaming_resp.raise_for_status()

        for chunk in streaming_resp.iter_content(chunk_size):
            output_file.write(chunk)
            bytes_read += len(chunk)

    return bytes_read
