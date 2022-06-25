from __future__ import annotations

from collections.abc import Iterator
from contextlib import suppress
from dataclasses import dataclass
from enum import Enum
from enum import unique
from pathlib import Path
from shutil import move
from textwrap import indent
from typing import Any

from IPython.display import display
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
from photos.utilities import is_jpg
from photos.utilities import make_thumbnail
from photos.utilities import open_image


class Organizer:
    """Base class for the organizer."""

    __slots__ = ("_dir", "_data", "_rotate")

    def __init__(self) -> None:
        super().__init__()
        self._dir: Path | None = None
        self._data: _Data | None = None
        self._rotate: int = 0

    # properties

    @property
    def data(self) -> _Data:
        if (data := self._data) is None:
            raise ValueError(f"{self._data=}")
        return data

    @property
    def dir(self) -> Path:
        if (dir := self._dir) is None:
            raise ValueError(f"{self._dir=}")
        return dir

    # methods

    def start(self, dir: PathLike = PATH_CAMERA_UPLOADS, /) -> None:
        self._dir = Path(dir)
        while True:
            try:
                self._get_next_data()
            except _NoNextFileError:
                logger.info("No more files found in {}", self.dir)
                return
            else:
                if self._loop_choices() is _Choice.quit:
                    return

    def _choice_delete(self) -> None:
        logger.warning("Deleting {}", path := self.data.path)
        path.unlink()
        self._get_next_data()

    def _choice_overview(self) -> None:
        display(make_thumbnail(self.data.image.rotate(self._rotate)))

        def yield_metadata() -> Iterator[tuple[str, Any]]:
            data = self.data
            yield "path", data.path
            yield "file size", data.file_size
            if (datetime_data := data.datetime_data) is None:
                yield "datetime", None
            else:
                yield "datetime", datetime_data.value
                yield "source", datetime_data.source
            yield "resolution", data.resolution
            yield "destination", data.destination

        self._log("Metadata", yield_metadata())

    def _choice_move(self) -> None:
        if (dest := (data := self.data).destination) is None:
            raise RuntimeError("Cannot call 'MOVE' when destination is missing")
        self._log("Moving", [("from", fr := data.path), ("destination", dest)])
        move(fr, dest)
        self._get_next_data()

    def _choice_rotate_180(self) -> None:
        self._rotate = 180
        self._choice_overview()

    def _choice_rotate_clockwise(self) -> None:
        self._rotate = 90
        self._choice_overview()

    def _choice_rotate_anticlockwise(self) -> None:
        self._rotate = -90
        self._choice_overview()

    def _choice_tags(self) -> None:
        self._log("Tags", self.data.tags.items())

    def _get_choice(self) -> _Choice:
        choices = {
            c.value: c.name
            for c in _Choice
            if (c is not _Choice.move)
            or (c is _Choice.move and self.data.destination is not None)
        }
        while True:
            self._log("Select your choice:", choices.items())
            with suppress(KeyError):
                return _Choice[choices[input("> ")]]

    def _get_next_data(self) -> None:
        try:
            path = next(p for p in sorted(self.dir.iterdir()) if is_jpg(p))
        except StopIteration:
            raise _NoNextFileError from None
        else:
            self._data = _Data(path)
            self._choice_overview()

    def _log(self, summary: str, details: Any, /) -> None:
        tabulated = indent(tabulate(details), 10 * " ")
        logger.info("{}:\n{}", summary, tabulated)

    def _loop_choices(self) -> _Choice:
        while True:
            if (choice := self._get_choice()) is _Choice.overview:
                self._choice_overview()
            elif choice is _Choice.rotate_180:
                self._choice_rotate_180()
            elif choice is _Choice.rotate_clockwise:
                self._choice_rotate_clockwise()
            elif choice is _Choice.rotate_anticlockwise:
                self._choice_rotate_anticlockwise()
            elif choice is _Choice.tags:
                self._choice_tags()
            elif choice is _Choice.move:
                self._choice_move()
            elif choice is _Choice.delete:
                self._choice_delete()
            elif choice is _Choice.quit:
                return choice
            else:
                raise ValueError(f"Invalid {choice=}")


class _NoNextFileError(FileNotFoundError):
    ...


@dataclass
class _Data:
    path: Path

    def __post_init__(self) -> None:
        self.image = image = open_image(path := self.path)
        self.file_size = naturalsize(get_file_size(path))
        self.datetime_data = datetime_data = get_datetime_data(image, path)
        self.resolution = get_resolution(image)
        self.tags = get_parsed_exif_tags(image)
        self.destination = get_destination(datetime_data)


@unique
class _Choice(Enum):
    overview = "o"
    rotate_180 = "r"
    rotate_clockwise = "rr"
    rotate_anticlockwise = "rl"
    tags = "t"
    move = "m"
    delete = "d"
    quit = "q"


ORGANIZER = Organizer()
