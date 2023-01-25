import datetime as dt
from collections.abc import Iterator
from functools import cache
from pathlib import Path
from typing import cast

from hypothesis import given
from hypothesis.strategies import SearchStrategy, sampled_from
from luigi import DateMinuteParameter, Event, LocalTarget, Task, build
from pandas import read_pickle, to_pickle
from PIL.Image import Image
from utilities.atomicwrites import writer
from utilities.datetime import UTC
from utilities.hypothesis import assume_does_not_raise
from utilities.tempfile import gettempdir

from photos.constants import (
    PATH_CAMERA_UPLOADS,
    PATH_GOOGLE_DOWNLOAD,
    PATH_PHOTOS,
)
from photos.utilities import is_supported, open_image_pillow


class GetPaths(Task):
    as_of = cast(
        dt.datetime,
        DateMinuteParameter(interval=30, default=dt.datetime.now(tz=UTC)),
    )

    def output(self) -> LocalTarget:
        return LocalTarget(
            gettempdir().joinpath(
                type(self).__name__,
                f"{self.as_of:%Y%m%d%H%M%S}.gz",
            ),
        )

    def run(self) -> None:
        def yield_paths() -> Iterator[Path]:
            for path in {
                PATH_CAMERA_UPLOADS,
                PATH_GOOGLE_DOWNLOAD,
                PATH_PHOTOS,
            }:
                for p in path.rglob("*"):
                    if p.is_file() and is_supported(p):
                        yield p

        paths = list(yield_paths())
        with writer(self.output().path, overwrite=True) as temp:
            to_pickle(paths, temp)


@GetPaths.event_handler(Event.SUCCESS)
def _(task: GetPaths, /) -> None:
    files = sorted(Path(task.output().path).parent.iterdir(), reverse=True)
    for old in files[1:]:
        old.unlink(missing_ok=True)


@cache
def _get_paths() -> list[Path]:
    _ = build([task := GetPaths()], local_scheduler=True)
    return read_pickle(task.output().path)


def paths() -> SearchStrategy[Path]:
    return sampled_from(_get_paths()).filter(lambda x: x.exists())


@given(path=paths())
def test_paths(path: Path) -> None:
    with assume_does_not_raise(FileNotFoundError):
        assert isinstance(path, Path)
        assert path.is_file()
        assert is_supported(path)


def images() -> SearchStrategy[Image]:
    with assume_does_not_raise(FileNotFoundError):
        return paths().map(open_image_pillow)


@given(image=images())
def test_images(image: Image) -> None:
    assert isinstance(image, Image)
