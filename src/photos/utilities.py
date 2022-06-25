import datetime as dt
from contextlib import suppress
from pathlib import Path
from typing import Any
from typing import Optional

from PIL.ExifTags import TAGS
from PIL.Image import Image
from PIL.Image import open as _open
from dycw_utilities.pathlib import PathLike
from dycw_utilities.pathlib import ensure_suffix

from photos.constants import PATH_MONTHLY


def get_datetime(image: Image, /) -> Optional[dt.datetime]:
    return get_parsed_exif_tags(image).get("DateTime")


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
    datetime: dt.datetime,
    /,
    *,
    root: PathLike = PATH_MONTHLY,
    suffix: str = ".jpg",
) -> Path:
    path = Path(root).joinpath(
        datetime.strftime("%Y-%m"), datetime.strftime("%Y-%m-%d %H:%M:%S")
    )
    return ensure_suffix(path, suffix)


def get_file_size(path: PathLike, /) -> int:
    return Path(path).stat().st_size


def get_raw_exif_tags(image: Image, /) -> dict[str, Any]:
    return {TAGS[k]: v for k, v in image.getexif().items() if k in TAGS}


def get_resolution(image: Image, /) -> tuple[int, int]:
    return image.size


def is_jpg(path: PathLike, /) -> bool:
    return Path(path).suffix == ".jpg"


def open_image(path: PathLike, /) -> Image:
    with open(path, mode="rb") as file:
        return _open(file)
