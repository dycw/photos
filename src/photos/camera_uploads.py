from __future__ import annotations

from collections.abc import Iterator
from contextlib import suppress
from dataclasses import dataclass
from enum import Enum
from enum import unique
from pathlib import Path
from typing import Any

from boltons.fileutils import atomic_rename
from humanize import naturalsize
from IPython.display import display
from loguru import logger
from tabulate import tabulate
from utilities.pathlib import PathLike
from utilities.typing import never

from photos.constants import PATH_CAMERA_UPLOADS
from photos.utilities import get_file_size
from photos.utilities import get_parsed_exif_tags
from photos.utilities import get_path_monthly
from photos.utilities import get_path_stash
from photos.utilities import get_paths_randomly
from photos.utilities import get_resolution
from photos.utilities import is_supported
from photos.utilities import make_thumbnail
from photos.utilities import open_image_pillow
from photos.utilities import purge_empty_directories


@unique
class _Choice(Enum):
    overview = "o"
    rotate_clockwise = "r"
    rotate_anticlockwise = "l"
    rotate_180 = "rr"
    tags = "t"
    move = "m"
    delete = "d"
    skip = "s"
    stash = "st"
    auto = "auto"
    quit_ = "q"


class Organizer:
    """Base class for the organizer."""

    __slots__ = ("_dir", "_data", "_rotate", "_skips")

    def __init__(self) -> None:
        super().__init__()
        self._dir: Path | None = None
        self._data: _Data | None = None
        self._rotate: int = 0
        self._skips: set[Path] = set()

    # properties

    @property
    def data(self) -> _Data:
        """The data."""
        if (data := self._data) is None:
            msg = f"{self._data=}"
            raise AttributeError(msg)
        return data

    @data.setter
    def data(self, value: _Data, /) -> None:
        self._data = value

    @property
    def dir_(self) -> Path:
        """The directory."""
        if (dir_ := self._dir) is None:
            msg = f"{self._dir=}"
            raise AttributeError(msg)
        return dir_

    @dir_.setter
    def dir_(self, value: Path, /) -> None:
        self._dir = Path(value)

    @property
    def rotate(self) -> int:
        """Rotate the image."""
        if (rotate := self._rotate) is None:
            msg = f"{self._rotate=}"
            raise AttributeError(msg)
        return rotate

    @rotate.setter
    def rotate(self, value: int, /) -> None:
        _, self._rotate = divmod(self._rotate + value, 360)

    @property
    def skips(self) -> set[Path]:
        """The skips so far."""
        if (skips := self._skips) is None:
            msg = f"{self._skips=}"
            raise AttributeError(msg)
        return skips

    # methods

    def start(self, dir_: PathLike = PATH_CAMERA_UPLOADS, /) -> None:
        """Start the organizer."""
        self.dir_ = Path(dir_)
        while True:
            try:
                self._get_next_data()
            except _NoNextFileError:
                break
            else:
                if self._loop_choices() is _Choice.quit_:
                    break
        purge_empty_directories(self.dir_)

    def _choice_auto(self) -> _Choice:
        while True:
            data = self.data
            dt_data = data.path_monthly
            try:
                if (dt_data is not None and dt_data.source == "EXIF") or (
                    data.tags.get("Make") == "Apple"
                ):
                    self._choice_move()
                else:
                    self._choice_stash()
            except _NoNextFileError:
                return _Choice.quit_

    def _choice_delete(self) -> None:
        path = self.data.path
        logger.info("\n\nDeleting:\n{}\n\n", tabulate([("path", path)]))
        path.unlink()
        self._get_next_data()

    def _choice_overview(self) -> None:
        _ = display(make_thumbnail(self.data.image.rotate(self._rotate)))

        def yield_metadata() -> Iterator[tuple[str, Any]]:
            data = self.data
            yield "path", data.path
            yield "file size", data.file_size
            yield "resolution", data.resolution
            yield "make", data.make
            yield "model", data.model
            yield "datetime", data.datetime
            yield "source", data.source
            yield "destination", data.destination

        logger.info("Metadata:\n{}", tabulate(yield_metadata()))

    def _choice_move(self) -> None:
        if (dest := (data := self.data).destination) is None:
            msg = "Cannot call 'MOVE' when destination is missing"
            raise RuntimeError(msg)
        path = data.path
        logger.info(
            "\n\nMoving:\n{}\n\n",
            tabulate([("from", path), ("destination", dest)]),
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        atomic_rename(path, dest)
        self._get_next_data()

    def _choice_rotate_180(self) -> None:
        self.rotate = 180
        self._choice_overview()

    def _choice_rotate_clockwise(self) -> None:
        self.rotate = -90
        self._choice_overview()

    def _choice_rotate_anticlockwise(self) -> None:
        self.rotate = 90
        self._choice_overview()

    def _choice_skip(self) -> None:
        path = self.data.path
        logger.info("\n\nSkipping:\n{}\n\n", tabulate([("path", path)]))
        self.skips.add(path := self.data.path)
        self._get_next_data()

    def _choice_stash(self) -> None:
        path = (data := self.data).path
        dest = data.path_stash
        logger.info(
            "\n\nStashing:\n{}\n\n",
            tabulate([("path", path), ("destination", dest)]),
        )
        dest.parent.mkdir(parents=True, exist_ok=True)
        atomic_rename(path, dest)
        self._get_next_data()

    def _choice_tags(self) -> None:
        logger.info("Tags:\n{}", tabulate(self.data.tags.items()))

    def _get_choice(self) -> _Choice:
        choices = {
            c.value: c.name
            for c in _Choice
            if (c is not _Choice.move)
            or (c is _Choice.move and self.data.destination is not None)
        }
        desc = ", ".join(f"{k}={v}" for k, v in choices.items())
        while True:
            logger.info("Select your choice: {}", desc)
            with suppress(KeyError):
                return _Choice[choices[input("> ").strip()]]

    def _get_next_data(self) -> None:
        try:
            path = next(
                p
                for p in get_paths_randomly(self.dir_)
                if p.is_file() and is_supported(p) and p not in self.skips
            )
        except StopIteration:
            logger.info("No more files found in {}", self.dir_)
            raise _NoNextFileError from None
        else:
            self.data = _Data(path)
            self._choice_overview()

    def _loop_choices(self) -> _Choice:  # noqa: C901
        while True:
            if (choice := self._get_choice()) is _Choice.overview:
                self._choice_overview()
            elif choice is _Choice.rotate_clockwise:
                self._choice_rotate_clockwise()
            elif choice is _Choice.rotate_anticlockwise:
                self._choice_rotate_anticlockwise()
            elif choice is _Choice.rotate_180:
                self._choice_rotate_180()
            elif choice is _Choice.tags:
                self._choice_tags()
            elif choice is _Choice.move:
                self._choice_move()
            elif choice is _Choice.delete:
                self._choice_delete()
            elif choice is _Choice.skip:
                self._choice_skip()
            elif choice is _Choice.stash:
                self._choice_stash()
            elif choice is _Choice.auto:
                return self._choice_auto()
            elif choice is _Choice.quit_:  # noqa: RET505
                return choice
            else:
                return never(choice)


class _NoNextFileError(FileNotFoundError):
    ...


@dataclass
class _Data:
    path: Path

    def __post_init__(self) -> None:
        self.image = image = open_image_pillow(path := self.path)
        self.file_size = naturalsize(get_file_size(path))
        self.resolution = get_resolution(image)
        self.tags = get_parsed_exif_tags(image)
        if (tags := self.tags) is None:
            self.make = None
            self.model = None
        else:
            self.make = tags.get("Make")
            self.model = tags.get("Model")
        self.path_monthly = get_path_monthly(path, image=image)
        if (pm := self.path_monthly) is None:
            self.datetime = None
            self.source = None
            self.destination = None
        else:
            self.datetime = pm.datetime
            self.source = pm.source
            self.destination = pm.destination
        self.path_stash = get_path_stash(path)


ORGANIZER = Organizer()
