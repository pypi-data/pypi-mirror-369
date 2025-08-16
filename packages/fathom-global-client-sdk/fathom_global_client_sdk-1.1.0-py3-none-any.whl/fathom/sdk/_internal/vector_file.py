import contextlib
import os
from typing import Any

import fiona

from fathom.sdk.exceptions import VectorFileError


def polygon_from_geopkg(geopkg_file_path: os.PathLike) -> dict:
    """Loads a polygon from a geopkg file at the given file path."""
    return polygon_from_vector_file(geopkg_file_path)


def polygon_from_shapefile(shapefile_path: os.PathLike) -> dict:
    """Loads a polygon from a shapefile at the given file path."""
    return polygon_from_vector_file(shapefile_path)


def polygon_from_vector_file(vector_file_path: os.PathLike) -> dict:
    """Load a generic vector file using fiona"""
    with contextlib.ExitStack() as stack:
        try:
            geopkg = stack.enter_context(fiona.open(os.fspath(vector_file_path)))
        except Exception as e:
            raise VectorFileError(
                f"Unable to load vector file '{vector_file_path}'"
            ) from e

        num_features = len(geopkg)
        if num_features != 1:
            raise VectorFileError(
                f"Expected exactly 1 feature in {vector_file_path}, got {num_features}"
            )

        feature: fiona.Feature = next(iter(geopkg))
        geometry: dict[str, Any] = fiona.model.to_dict(feature["geometry"])

        if geometry["type"] == "MultiPolygon":
            # extract a multipolygon manually if it's present. Saving a polygon from QGIS outputs it as a
            # multipolygon even if there's only 1 ring, so do this to save the user some hassle.
            num_polygons = len(geometry["coordinates"][0])
            if num_polygons != 1:
                raise VectorFileError(f"Expected exactly 1 polygon, got {num_polygons}")

            geometry["type"] = "Polygon"
            geometry["coordinates"] = geometry["coordinates"][0]

            # Might still have interior rings but it will be handled on the API side
        elif geometry["type"] != "Polygon":
            raise VectorFileError(
                f"""Expected geometry to be 'Polygon' but was '{geometry["type"]}'"""
            )

        return geometry
