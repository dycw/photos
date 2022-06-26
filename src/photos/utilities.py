from __future__ import annotations

import datetime as dt
from contextlib import suppress
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path
from random import shuffle
from re import search
from shutil import rmtree
from typing import Any
from typing import Literal
from typing import get_args
from typing import get_origin

import pyexiv2
from PIL.ExifTags import TAGS
from PIL.Image import Image
from PIL.Image import open as _open
from PIL.ImageOps import contain
from dycw_utilities.pathlib import PathLike
from dycw_utilities.pathlib import ensure_suffix
from dycw_utilities.re import extract_group
from loguru import logger
from typeguard import typechecked

from photos.constants import EXIF_TAGS_PYEXVI2
from photos.constants import PATH_MONTHLY
from photos.constants import PATH_STASH
from photos.constants import THUMBNAIL_SIZE
from photos.types import FractionOrZero
from photos.types import Zero


def get_file_size(path: PathLike, /) -> int:
    return Path(path).stat().st_size


def get_parsed_exif_tags(path: PathLike, image: Image, /) -> dict[str, Any]:
    return get_parsed_exif_tags_pillow(image) | get_parsed_exif_tags_pyexiv2(
        path
    )


def get_parsed_exif_tags_pillow(image: Image, /) -> dict[str, Any]:
    tags = get_raw_exif_tags_pillow(image)
    for key in {"DateTime"}:
        with suppress(KeyError):
            tags[key] = dt.datetime.strptime(tags[key], "%Y:%m:%d %H:%M:%S")
    for key in {"XResolution", "YResolution"}:
        with suppress(KeyError):
            tags[key] = float(tags[key])
    return tags


def get_parsed_exif_tags_pyexiv2(path: PathLike, /) -> dict[str, Any]:
    tags = {
        k: v
        for k, v in get_raw_exif_tags_pyexiv2(path).items()
        if k != "" and not is_hex(k)
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


def get_path_monthly(
    path: PathLike,
    /,
    *,
    image: Image | None = None,
    raise_if_missing: bool = True,
) -> PathMonthly | None:
    path = Path(path)
    if image is None:
        try:
            image = open_image(path)
        except FileNotFoundError:
            if raise_if_missing:
                raise
        else:
            with suppress(KeyError):
                date = get_parsed_exif_tags(image)["DateTime"]
                return PathMonthly(path, date, "EXIF")
    for pattern, fmt in [
        (r"(\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2})", "%Y-%m-%d %H.%M.%S"),
        (r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", "%Y-%m-%d %H:%M:%S"),
    ]:
        with suppress(ValueError):
            as_str = extract_group(pattern, path.name)
            date = dt.datetime.strptime(as_str, fmt)
            return PathMonthly(path, date, "filename")
    return None


@dataclass
class PathMonthly:
    path: Path
    datetime: dt.datetime
    source: Literal["EXIF", "filename"]

    def __post_init__(self) -> None:
        date = self.datetime
        self.destination = ensure_suffix(
            PATH_MONTHLY.joinpath(
                date.strftime("%Y-%m"), date.strftime("%Y-%m-%d %H:%M:%S")
            ),
            self.path.suffix,
        )


def get_path_stash(path: Path, /) -> Path:
    return PATH_STASH.joinpath(path.name)


def get_paths_randomly(path: PathLike, /) -> list[Path]:
    paths = list(Path(path).rglob("*"))
    shuffle(paths)
    return paths


def get_raw_exif_tags_pillow(image: Image, /) -> dict[str, Any]:
    return {TAGS[k]: v for k, v in image.getexif().items() if k in TAGS}


def get_raw_exif_tags_pyexiv2(path: PathLike, /) -> dict[str, Any]:
    image = pyexiv2.Image(Path(path).as_posix())
    return image.read_exif()


def get_resolution(image: Image, /) -> tuple[int, int]:
    return image.size


def is_instance(obj: Any, cls: Any, /) -> bool:
    try:
        return isinstance(obj, cls)
    except TypeError:
        try:

            @typechecked
            def func(_: cls, /) -> None:
                ...

            func(obj)
            return True
        except TypeError:
            return False


def is_hex(text: str, /) -> bool:
    return bool(search(r"0x\w{4}", text))


def is_jpg(path: PathLike, /) -> bool:
    return Path(path).suffix == ".jpg"


def is_png(path: PathLike, /) -> bool:
    return Path(path).suffix == ".png"


def is_supported(path: PathLike, /) -> bool:
    return is_jpg(path) or is_png(path)


def open_image(path: PathLike, /) -> Image:
    with open(path, mode="rb") as file:
        image = _open(file)
        image.load()
    return image


def make_thumbnail(image: Image, /) -> Image:
    return contain(image, THUMBNAIL_SIZE)


def purge_empty_directories(path: PathLike, /) -> None:
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
    if date == "0000:00:00":
        return dt.date.min
    elif search(r"^\d{2}\d{2}$", date):
        return dt.datetime.strptime(date, "%y%m").date()
    elif search(r"^\d{4}:\d{2}:\d{3}$", date):
        return to_date(date[:-1])
    else:
        return dt.datetime.strptime(date, "%Y:%m:%d").date()


def to_datetime(date: str, /) -> dt.datetime:
    if date == "9999:99:99 00:00:00":
        return dt.datetime.max
    else:
        return dt.datetime.strptime(date, "%Y:%m:%d %H:%M:%S")


def to_fraction_or_zero(frac: str, /) -> FractionOrZero:
    try:
        return Fraction(frac)
    except ZeroDivisionError:
        return Zero()


def write_datetime(path: PathLike, datetime: dt.datetime, /) -> None:
    image = pyexiv2.Image(Path(path).as_posix())
    image.modify_exif(
        {"Exif.Image.DateTime": datetime.strftime("%4Y:%m:%d %H:%M:%S")}
    )
