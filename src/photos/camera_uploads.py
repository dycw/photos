from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path
from shutil import copy
from shutil import move
from typing import Any

from IPython.display import display
from PIL.Image import open as open_image
from dycw_utilities.pathlib import PathLike
from humanize import naturalsize
from loguru import logger
from tabulate import tabulate

from photos.constants import PATH_CAMERA_UPLOADS
from photos.utilities import get_datetime_data
from photos.utilities import get_destination
from photos.utilities import get_file_size
from photos.utilities import get_parsed_exif_tags
from photos.utilities import get_resolution
from photos.utilities import make_thumbnail


def try_get_next_jpg() -> Path | None:
    it = (
        path
        for path in sorted(PATH_CAMERA_UPLOADS.iterdir())
        if path.as_posix().endswith(".jpg")
    )
    return next(it, None)


@dataclass(repr=False)
class Viewer:
    """Class for processing a JPG."""

    path: PathLike

    # private

    def __post_init__(self) -> None:
        self._file_size = get_file_size(path := self.path)
        self._image = open_image(path)
        self._datetime_data = get_datetime_data(path)
        self._destination = get_destination(self._datetime_data)
        self._thumbnail = make_thumbnail(self._image)
        self._resolution = get_resolution(self._image)
        self._tags = get_parsed_exif_tags(self._image)

    def __repr__(self) -> str:
        display(self._thumbnail)
        return tabulate(list(self._yield_metadata()))

    def _yield_metadata(self) -> Iterator[tuple[str, Any]]:
        yield "path", self.path
        yield "file size", naturalsize(self._file_size)
        if (datetime_data := self._datetime_data) is None:
            yield "datetime", None
        else:
            yield "datetime", datetime_data.value
            yield "source", datetime_data.source
        yield "resolution", self._resolution
        yield "destination", self._destination

    # public

    def copy(self) -> None:
        if (destination := self._destination) is None:
            raise ValueError(f"{destination=}")
        else:
            copy(source := self.path, destination)
            logger.info("Copied:\n    {}\n--> {}", source, destination)
        globals()["V"] = Viewer.next()

    @classmethod
    def next(cls) -> Viewer:
        if (path := try_get_next_jpg()) is None:
            raise ValueError(f"{path=}")
        return cls(path)

    def move(self) -> None:
        if (destination := self._destination) is None:
            raise ValueError(f"{destination=}")
        else:
            move(source := self.path, destination)
            logger.info("Copied:\n    {}\n--> {}", source, destination)
        globals()["V"] = Viewer.next()
