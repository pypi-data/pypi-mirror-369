import itertools
import os
import pathlib
import tempfile
import zipfile
from collections.abc import Generator

import pygeoif
from fastkml import kml

from fathom.sdk.exceptions import KMLError


def _load_kml_features(
    container: kml.kml_children,
) -> Generator[kml.Placemark, None, None]:
    """Recursively iterate through the XML tree, yielding Placemarks

    presentation-only types are ignored - overlays, styles, etc.
    """
    if isinstance(container, kml.Placemark):
        yield container
        return

    for f in container.features:
        if isinstance(f, kml.Placemark):
            yield f
        elif isinstance(f, kml.Document):
            for g in f.features:
                yield from _load_kml_features(g)
        elif isinstance(f, kml.Folder):
            for g in f.features:
                yield from _load_kml_features(g)


def polygon_from_kml(kml_file_path: os.PathLike) -> dict:
    """Loads a polygon from a kml file at the given file path."""
    try:
        with open(kml_file_path, "rb") as kml_file:
            k: kml.KML = kml.KML.class_from_string(kml_file.read())
    except Exception as e:
        raise KMLError(f"Unable to load KML file '{kml_file_path}'") from e

    features = list(
        itertools.chain.from_iterable(_load_kml_features(f) for f in k.features)
    )

    num_features = len(features)
    if num_features != 1:
        raise KMLError(
            f"Expected exactly 1 feature in {kml_file_path}, got {num_features}"
        )

    feature = features[0]

    if not isinstance(feature.geometry, pygeoif.Polygon):
        raise KMLError(
            f"Expected geometry to be '{pygeoif.Polygon}' but was '{type(feature.geometry)}'"
        )

    # __geo_interface__ is a dict conforming to the GeoJSON spec
    return feature.geometry.__geo_interface__


def polygon_from_kmz(kmz_file_path: os.PathLike) -> dict:
    """Loads a polygon from a kmz file at the given file path.

    It assumes that kmz file path contains exactly one kml file.
    """
    with tempfile.TemporaryDirectory() as kmz_contents:
        with zipfile.ZipFile(kmz_file_path) as zip_contents:
            zip_contents.extractall(kmz_contents)

        for root, _, files in os.walk(kmz_contents):
            for file in files:
                if file.endswith(".kml"):
                    return polygon_from_kml(pathlib.PurePath(os.path.join(root, file)))

    raise KMLError(f"No '.kml' file found in {kmz_file_path}")
