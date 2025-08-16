import functools
import io
import json
import os
import pathlib
from typing import Any

from fathom.sdk.exceptions import GeoJSONError


@functools.singledispatch
def load_geojson(
    geojson: os.PathLike
    | str
    | bytes
    | bytearray
    | io.BufferedIOBase
    | io.TextIOBase
    | dict,
) -> dict:
    raise NotImplementedError(f"Cannot load geojson from {type(geojson)}")


@load_geojson.register(os.PathLike)
def load_geojson_path(
    geojson: os.PathLike,
) -> dict:
    return json.loads(pathlib.Path(geojson).read_text())


@load_geojson.register(str)
@load_geojson.register(bytes)
@load_geojson.register(bytearray)
def load_geojson_string(
    geojson: str | bytes | bytearray,
) -> dict:
    if isinstance(geojson, str) and os.path.exists(geojson):
        raise GeoJSONError(
            "When passing a filepath to a GeoJSON file, the argument should be wrapped using `pathlib.Path`"
        )

    return json.loads(geojson)


@load_geojson.register(io.BufferedIOBase)
@load_geojson.register(io.TextIOBase)
def load_geojson_buffer(
    geojson: io.BufferedIOBase | io.TextIOBase,
) -> dict:
    return json.load(geojson)


@load_geojson.register(dict)
def load_geojson_dict(
    geojson: dict,
) -> dict:
    return geojson


def polygon_from_geojson(geojson: Any) -> dict:
    """Loads the geojson from the given object - polygon verification is done server-side"""
    return load_geojson(geojson)
