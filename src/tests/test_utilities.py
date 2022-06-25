import datetime as dt
from itertools import chain
from pathlib import Path

from PIL.Image import Image
from dycw_utilities.hypothesis import assume_does_not_raise
from hypothesis import given
from tabulate import tabulate

from photos.utilities import get_datetime_data
from photos.utilities import get_file_size
from photos.utilities import get_parsed_exif_tags
from photos.utilities import get_raw_exif_tags
from photos.utilities import get_resolution
from photos.utilities import open_image
from tests.test_strategies import jpg_images
from tests.test_strategies import jpg_paths


@given(path=jpg_paths())
def test_get_datetime_data(path: Path) -> None:
    with assume_does_not_raise(FileNotFoundError):
        _ = get_datetime_data(path)


@given(path=jpg_paths())
def test_get_file_sizes(path: Path) -> None:
    with assume_does_not_raise(FileNotFoundError):
        _ = get_file_size(path)


@given(image=jpg_images())
def test_get_parsed_exif_tags(image: Image) -> None:
    with assume_does_not_raise(FileNotFoundError):
        tags = get_parsed_exif_tags(image)
    expected = {
        "Artist": str,
        "RelatedImageWidth": int,
        "RelatedImageLength": int,
        "TileWidth": int,
        "DateTime": dt.datetime,
        "ExifOffset": int,
        "GPSInfo": int,
        "HostComputer": str,
        "ImageDescription": str,
        "Make": str,
        "Model": str,
        "Orientation": int,
        "PrintImageMatching": bytes,
        "ResolutionUnit": int,
        "Software": str,
        "XResolution": float,
        "YCbCrPositioning": int,
        "YCbCrSubSampling": tuple,
        "YResolution": float,
        "TileLength": int,
        "Copyright": str,
        "ImageWidth": int,
        "CustomRendered": int,
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
    with assume_does_not_raise(FileNotFoundError):
        _ = get_raw_exif_tags(image)


@given(image=jpg_images())
def test_get_resolution(image: Image) -> None:
    with assume_does_not_raise(FileNotFoundError):
        _ = get_resolution(image)


@given(path=jpg_paths())
def test_open_image(path: Path) -> None:
    with assume_does_not_raise(FileNotFoundError):
        _ = open_image(path)
