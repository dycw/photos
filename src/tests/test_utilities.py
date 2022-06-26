import datetime as dt
from itertools import chain
from pathlib import Path
from re import search
from shutil import copy
from typing import Any

from PIL.Image import Image
from dycw_utilities.hypothesis import assume_does_not_raise
from dycw_utilities.hypothesis.tempfile import temp_dirs
from dycw_utilities.tempfile import TemporaryDirectory
from dycw_utilities.tempfile import gettempdir
from git.repo import Repo
from hypothesis import given
from hypothesis.strategies import datetimes
from pytest import mark
from tabulate import tabulate

from photos.constants import EXIF_TAGS_PILLOW
from photos.constants import EXIF_TAGS_PYEXVI2
from photos.constants import PATH_MONTHLY
from photos.constants import PATH_STASH
from photos.utilities import PathMonthly
from photos.utilities import get_file_size
from photos.utilities import get_parsed_exif_tags
from photos.utilities import get_parsed_exif_tags_pillow
from photos.utilities import get_parsed_exif_tags_pyexiv2
from photos.utilities import get_path_monthly
from photos.utilities import get_path_stash
from photos.utilities import get_raw_exif_tags_pillow
from photos.utilities import get_raw_exif_tags_pyexiv2
from photos.utilities import get_resolution
from photos.utilities import is_instance
from photos.utilities import open_image
from photos.utilities import write_datetime
from tests.test_strategies import images
from tests.test_strategies import paths


@given(path=paths())
def test_get_file_sizes(path: Path) -> None:
    with assume_does_not_raise(FileNotFoundError):
        _ = get_file_size(path)


@given(image=images())
def test_get_parsed_exif_tags_pillow(image: Image) -> None:
    with assume_does_not_raise(FileNotFoundError):
        tags = get_parsed_exif_tags_pillow(image)
    for key, value in tags.items():
        data = [("key", key), ("value", value), ("type", type(value))]
        assert key in EXIF_TAGS_PILLOW, f"No expected type:\n{tabulate(data)}"
        exp = EXIF_TAGS_PILLOW[key]
        assert is_instance(value, exp), "Type error:\n{}".format(
            tabulate(chain(data, [("expected", exp)]))
        )


@given(path=paths())
def test_get_parsed_exif_tags_pyexiv2(path: Path) -> None:
    with assume_does_not_raise(FileNotFoundError):
        tags = get_parsed_exif_tags_pyexiv2(path)
    for key, value in tags.items():
        data = [("key", key), ("value", value), ("type", type(value))]
        assert key in EXIF_TAGS_PYEXVI2, f"No expected type:\n{tabulate(data)}"
        exp = EXIF_TAGS_PYEXVI2[key]
        assert is_instance(value, exp), "Type error:\n{}".format(
            tabulate(chain(data, [("expected", exp)]))
        )


class TestGetPathMonthly:
    @given(path=paths())
    def test_generic(self, path: Path) -> None:
        with assume_does_not_raise(FileNotFoundError):
            maybe = get_path_monthly(path)
        if isinstance(pm := maybe, PathMonthly):
            assert (dest := pm.destination).relative_to(PATH_MONTHLY)
            parts = dest.parts
            assert search(r"^\d{4}-\d{2}$", parts[-2])
            assert search(
                r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.jpg$", parts[-1]
            )

    def test_specific(self) -> None:
        path = gettempdir().joinpath("2000-01-01 12:34:56.txt")
        result = get_path_monthly(path, raise_if_missing=False)
        assert result is not None
        expected = PathMonthly(
            path, dt.datetime(2000, 1, 1, 12, 34, 56), "filename"
        )
        assert result == expected
        assert result.destination == PATH_MONTHLY.joinpath(
            "2000-01", "2000-01-01 12:34:56.txt"
        )


@given(path=paths())
def test_get_path_stash(path: Path) -> None:
    with assume_does_not_raise(FileNotFoundError):
        p = get_path_stash(path)
    assert p.relative_to(PATH_STASH)
    assert path.name == p.name


@given(image=images())
def test_get_raw_exif_tags_pillow(image: Image) -> None:
    with assume_does_not_raise(FileNotFoundError):
        _ = get_raw_exif_tags_pillow(image)


@given(path=paths())
def test_get_raw_exif_tags_pyexiv2(path: Path) -> None:
    with assume_does_not_raise(FileNotFoundError):
        _ = get_raw_exif_tags_pyexiv2(path)


@given(image=images())
def test_get_resolution(image: Image) -> None:
    with assume_does_not_raise(FileNotFoundError):
        _ = get_resolution(image)


@mark.parametrize(
    ["obj", "cls", "expected"],
    [
        (0, int, True),
        (0, float, False),
        ([], list[int], True),
        ([1, 2, 3], list[int], True),
        ([1, 2, "3"], list[int], False),
    ],
)
def test_is_instance(obj: Any, cls: Any, expected: bool) -> None:
    assert is_instance(obj, cls) is expected


@given(path=paths())
def test_open_image(path: Path) -> None:
    with assume_does_not_raise(FileNotFoundError):
        _ = open_image(path)


@given(
    temp_dir=temp_dirs(),
    datetime=datetimes().filter(lambda x: x.microsecond == 0),
)
def test_write_datetime(
    temp_dir: TemporaryDirectory, datetime: dt.datetime
) -> None:
    repo = Repo(".", search_parent_directories=True)
    assert (root := repo.working_tree_dir) is not None
    src = Path(root, "src", "tests", "assets", "2020-09-25 20.18.18.png")
    dest = temp_dir.name.joinpath("temp")
    copy(src, dest)
    tags1 = get_parsed_exif_tags(open_image(dest))
    assert "DateTime" not in tags1
    write_datetime(dest, datetime)
    tags2 = get_parsed_exif_tags(open_image(dest))
    assert tags2["DateTime"] == datetime
    assert src.stat().st_size < dest.stat().st_size
