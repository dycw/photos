from __future__ import annotations

import datetime as dt
from contextlib import suppress
from dataclasses import dataclass
from datetime.timezone import utc
from fractions import Fraction
from pathlib import Path
from random import shuffle
from re import search
from shutil import rmtree
from typing import Any, Literal, get_args, get_origin

import pyexiv2
from beartype.door import die_if_unbearable
from beartype.roar import BeartypeAbbyHintViolation
from loguru import logger
from PIL.ExifTags import TAGS
from PIL.Image import Image as PILImage
from PIL.Image import open as _open
from PIL.ImageOps import contain
from pyexiv2 import Image as pyexiv2Image
from utilities.pathlib import PathLike, ensure_suffix
from utilities.re import extract_group

from photos.constants import (
    EXIF_TAGS_PYEXVI2,
    PATH_MONTHLY,
    PATH_STASH,
    PATHS_BAD_EXIF,
    THUMBNAIL_SIZE,
)
from photos.types import FractionOrZero, Zero


def get_file_size(path: PathLike, /) -> int:
    """Get the size of a file."""
    return Path(path).stat().st_size


def get_parsed_exif_tags(path: PathLike, /) -> dict[str, Any]:
    """Get the parsed EXIF tags of a file."""
    return get_parsed_exif_tags_pillow(path) | get_parsed_exif_tags_pyexiv2(
        path,
    )


def get_parsed_exif_tags_pillow(path: PathLike, /) -> dict[str, Any]:
    """Get the parsed EXIF tags of a file using Pillow."""
    tags = get_raw_exif_tags_pillow(path)
    for key in {"DateTime"}:
        with suppress(KeyError):
            tags[key] = dt.datetime.strptime(
                tags[key],
                "%Y:%m:%d %H:%M:%S",
            ).astimezone(utc)
    for key in {"XResolution", "YResolution"}:
        with suppress(KeyError):
            tags[key] = float(tags[key])
    return tags


def get_parsed_exif_tags_pyexiv2(  # noqa: C901
    path: PathLike,
    /,
) -> dict[str, Any]:
    """Get the parsed EXIF tags of a file using pyexiv2."""
    tags = {
        k: v
        for k, v in get_raw_exif_tags_pyexiv2(path).items()
        if not is_hex(k) and v != ""
    }
    for key, cls in EXIF_TAGS_PYEXVI2.items():
        try:
            text = tags[key]
        except KeyError:
            pass
        else:
            if cls is int:
                tags[key] = int(text)
            elif cls is FractionOrZero:
                tags[key] = to_fraction_or_zero(text)
            elif cls is dt.date:
                tags[key] = to_date(text)
            elif cls is dt.datetime:
                tags[key] = to_datetime(text)
            elif get_origin(cls) is list:
                (cls,) = get_args(cls)
                if cls is int:
                    tags[key] = list(map(int, text.split()))
                elif cls is FractionOrZero:
                    tags[key] = list(map(to_fraction_or_zero, text.split()))
    return tags


def get_datetime(path: PathLike, /) -> dt.datetime | None:
    """Get the datetime of a file."""
    raise NotImplementedError(path)


def get_path_monthly(path: PathLike, /) -> PathMonthly | None:
    """Get the monthly path of a file."""
    path = Path(path)
    with suppress(KeyError):
        date = get_parsed_exif_tags(path)["DateTime"]
        return PathMonthly(path, date, "EXIF")
    for pattern, fmt in [
        (r"(\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2})", "%Y-%m-%d %H.%M.%S"),
        (r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", "%Y-%m-%d %H:%M:%S"),
    ]:
        with suppress(ValueError):
            as_str = extract_group(pattern, path.name)
            date = dt.datetime.strptime(as_str, fmt).astimezone(utc)
            return PathMonthly(path, date, "filename")
    return None


@dataclass
class PathMonthly:
    """Collection of data regarding a monthly file."""

    path: Path
    datetime: dt.datetime
    source: Literal["EXIF", "filename"]

    def __post_init__(self) -> None:
        date = self.datetime
        self.destination = ensure_suffix(
            PATH_MONTHLY.joinpath(
                date.strftime("%Y-%m"),
                date.strftime("%Y-%m-%d %H:%M:%S"),
            ),
            self.path.suffix,
        )


def get_path_stash(path: Path, /) -> Path:
    """Get the path to the stash."""
    return PATH_STASH.joinpath(path.name)


def get_paths_randomly(path: PathLike, /) -> list[Path]:
    """Get the paths randomly."""
    paths = list(Path(path).rglob("*"))
    shuffle(paths)
    return paths


def get_raw_exif_tags_pillow(path: PathLike, /) -> dict[str, Any]:
    """Get the raw EXIF tags using Pillow."""
    return {
        TAGS[k]: v
        for k, v in open_image_pillow(path).getexif().items()
        if k in TAGS
    }


def get_raw_exif_tags_pyexiv2(path: PathLike, /) -> dict[str, Any]:
    """Get the raw EXIF tags using pyexiv2."""
    return open_image_pyexiv2(path).read_exif()


def get_resolution(image: PILImage, /) -> tuple[int, int]:
    """Get the resolution of an image."""
    return image.size


def is_bad_exif(path: PathLike, /) -> bool:
    """Check if a path is bad."""
    return Path(path) in PATHS_BAD_EXIF


def is_instance(obj: Any, cls: Any, /) -> bool:
    """Check if an object has the required type."""
    try:
        die_if_unbearable(obj, cls)
    except BeartypeAbbyHintViolation:
        return False
    else:
        return True


def is_hex(text: str, /) -> bool:
    """Check if a str is hex."""
    return bool(search(r"0x\w{4}", text))


def is_jpg(path: PathLike, /) -> bool:
    """Check if a file is a JPG."""
    return Path(path).suffix == ".jpg"


def is_png(path: PathLike, /) -> bool:
    """Check if a file is a PNG."""
    return Path(path).suffix == ".png"


def is_supported(path: PathLike, /) -> bool:
    """Check if a file is supported."""
    return (is_jpg(path) or is_png(path)) and not is_bad_exif(path)


def open_image_pillow(path: PathLike, /) -> PILImage:
    """Open a Pillow image."""
    with Path(path).open(mode="rb") as file:
        image = _open(file)
        image.load()
    return image


def open_image_pyexiv2(path: PathLike, /) -> pyexiv2Image:
    """Open a pyexiv2 image."""
    return pyexiv2Image(Path(path).as_posix())


def make_thumbnail(image: PILImage, /) -> PILImage:
    """Make a thumbnail."""
    return contain(image, THUMBNAIL_SIZE)


def purge_empty_directories(path: PathLike, /) -> None:
    """Purge the empty directories under a path."""
    while True:
        try:
            p = next(
                p
                for p in get_paths_randomly(path)
                if p.is_dir() and len(list(p.iterdir())) == 0
            )
        except StopIteration:
            break
        else:
            logger.info("Purging:\n{}", p)
            rmtree(p)


def to_date(date: str, /) -> dt.date:
    """Parse a string into a date."""
    if date == "0000:00:00":
        return dt.date.min
    if search(r"^\d{2}\d{2}$", date):
        return dt.datetime.strptime(date, "%y%m").astimezone(utc).date()
    if search(r"^\d{4}:\d{2}:\d{3}$", date):
        return to_date(date[:-1])
    return dt.datetime.strptime(date, "%Y:%m:%d").astimezone(utc).date()


def to_datetime(date: str, /) -> dt.datetime:
    """Parse a string into a datetime."""
    if date == "0000:00:00 00:00:00":
        return dt.datetime.min
    if date == "9999:99:99 00:00:00":
        return dt.datetime.max
    return dt.datetime.strptime(date, "%Y:%m:%d %H:%M:%S").astimezone(utc)


def to_fraction_or_zero(frac: str, /) -> FractionOrZero:
    """Parse a string into a fraction or Zero."""
    try:
        return Fraction(frac)
    except ZeroDivisionError:
        return Zero()


def write_datetime(path: PathLike, datetime: dt.datetime, /) -> None:
    """Write a datetime to a file."""
    image = pyexiv2.Image(Path(path).as_posix())
    image.modify_exif(
        {"Exif.Image.DateTime": datetime.strftime("%4Y:%m:%d %H:%M:%S")},
    )
