from __future__ import annotations

from pathlib import Path

from hypothesis import given
from hypothesis.strategies import sampled_from

from google_photos.main import ALL_PATHS
from google_photos.main import ROOT
from google_photos.main import Type
from google_photos.main import View


def test_root() -> None:
    assert ROOT.is_dir()


def test_all_paths() -> None:
    assert len(ALL_PATHS) == 137552


st_paths = sampled_from(ALL_PATHS)


@given(path=st_paths)
def test_st_paths(path: Path) -> None:
    assert isinstance(path, Path)


st_files = st_paths.filter(lambda x: x.is_file())


@given(file=st_files)
def test_st_files(file: Path) -> None:
    assert file.is_file()


st_views = st_files.map(View)


@given(view=st_views)
def test_st_views(view: View) -> None:
    assert isinstance(view, View)
    assert isinstance(view.is_photo, bool)
    assert isinstance(view.type, Type)


st_photos = st_views.filter(lambda x: x.is_photo)


@given(photo=st_photos)
def test_st_photos(photo: View) -> None:
    assert photo.is_photo
