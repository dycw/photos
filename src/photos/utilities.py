from __future__ import annotations

import datetime as dt
from contextlib import suppress
from dataclasses import dataclass
from pathlib import Path
from random import shuffle
from shutil import rmtree
from typing import Any
from typing import Literal

from PIL.ExifTags import TAGS
from PIL.Image import Image
from PIL.Image import open as _open
from PIL.ImageOps import contain
from dycw_utilities.pathlib import PathLike
from dycw_utilities.pathlib import ensure_suffix
from dycw_utilities.re import extract_group
from loguru import logger

from photos.constants import PATH_MONTHLY
from photos.constants import THUMBNAIL_SIZE


def get_datetime_data(
    path: PathLike, /, *, image: Image | None = None
) -> DateTimeData | None:
    if image is None:
        image = open_image(path)
    with suppress(KeyError):
        value = get_parsed_exif_tags(image)["DateTime"]
        return DateTimeData(value=value, source="EXIF")
    name = Path(path).name
    for pattern, fmt in [
        (r"(\d{4}-\d{2}-\d{2} \d{2}\.\d{2}\.\d{2})", "%Y-%m-%d %H.%M.%S"),
        (r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", "%Y-%m-%d %H:%M:%S"),
    ]:
        with suppress(ValueError):
            as_str = extract_group(pattern, name)
            value = dt.datetime.strptime(as_str, fmt)
            return DateTimeData(value=value, source="filename")
    return None


@dataclass
class DateTimeData:
    value: dt.datetime
    source: Literal["EXIF", "filename"]


def get_parsed_exif_tags(image: Image, /) -> dict[str, Any]:
    tags = get_raw_exif_tags(image)
    for key in {"DateTime"}:
        with suppress(KeyError):
            tags[key] = dt.datetime.strptime(tags[key], "%Y:%m:%d %H:%M:%S")
    for key in {"XResolution", "YResolution"}:
        with suppress(KeyError):
            tags[key] = float(tags[key])
    return tags


def get_destination(
    data: DateTimeData | None,
    /,
    *,
    root: PathLike = PATH_MONTHLY,
    suffix: str = ".jpg",
) -> Path | None:
    if data is None:
        return None
    else:
        value = data.value
        path = Path(root).joinpath(
            value.strftime("%Y-%m"), value.strftime("%Y-%m-%d %H:%M:%S")
        )
        return ensure_suffix(path, suffix)


def get_file_size(path: PathLike, /) -> int:
    return Path(path).stat().st_size


def get_paths_randomly(path: PathLike, /) -> list[Path]:
    paths = list(Path(path).rglob("*"))
    shuffle(paths)
    return paths


def get_raw_exif_tags(image: Image, /) -> dict[str, Any]:
    return {TAGS[k]: v for k, v in image.getexif().items() if k in TAGS}


def get_resolution(image: Image, /) -> tuple[int, int]:
    return image.size


def is_jpg(path: PathLike, /) -> bool:
    return Path(path).suffix == ".jpg"


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
            path = next(
                p
                for p in get_paths_randomly(path)
                if p.is_dir() and len(list(p.iterdir())) == 0
            )
        except StopIteration:
            break
        else:
            logger.info("Purging:\n{}", path)
            rmtree(path)
