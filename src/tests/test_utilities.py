import datetime as dt
from itertools import chain
from pathlib import Path

from PIL.Image import Image
from hypothesis import given
from tabulate import tabulate

from photos.utilities import get_datetime
from photos.utilities import get_file_size
from photos.utilities import get_parsed_exif_tags
from photos.utilities import get_raw_exif_tags
from photos.utilities import get_resolution
from photos.utilities import open_image
from tests.test_strategies import jpg_images
from tests.test_strategies import jpg_paths


@given(image=jpg_images())
def test_get_datetime(image: Image) -> None:
    _ = get_datetime(image)


@given(path=jpg_paths())
def test_get_file_sizes(path: Path) -> None:
    _ = get_file_size(path)


@given(image=jpg_images())
def test_get_parsed_exif_tags(image: Image) -> None:
    tags = get_parsed_exif_tags(image)
    expected = {
        "DateTime": dt.datetime,
        "ExifOffset": int,
        "GPSInfo": int,
        "HostComputer": str,
        "Make": str,
        "Model": str,
        "Orientation": int,
        "ResolutionUnit": int,
        "Software": str,
        "XResolution": float,
        "YCbCrPositioning": int,
        "YResolution": float,
    }
    for key, value in tags.items():
        data = [("key", key), ("value", value), ("type", type(value))]
        assert key in expected, f"No expected type:\n{tabulate(data)}"
        exp = expected[key]
        assert isinstance(value, exp), "Type error:\n{}".format(
            tabulate(chain(data, [("expected", exp)]))
        )


@given(image=jpg_images())
def test_get_raw_exif_tags(image: Image) -> None:
    _ = get_raw_exif_tags(image)


@given(image=jpg_images())
def test_get_resolution(image: Image) -> None:
    _ = get_resolution(image)


@given(path=jpg_paths())
def test_open_image(path: Path) -> None:
    _ = open_image(path)
