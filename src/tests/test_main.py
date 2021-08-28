from __future__ import annotations

from google_photos.main import ALL_FILES
from google_photos.main import ALL_PATHS
from google_photos.main import ALL_VIEWS
from google_photos.main import ROOT
from google_photos.main import Type
from google_photos.main import View


def test_root() -> None:
    assert ROOT.is_dir()


def test_all_paths() -> None:
    assert len(ALL_PATHS) == 137552


def test_all_files() -> None:
    assert len(ALL_FILES) == 137147


def test_all_views() -> None:
    for view in ALL_VIEWS:
        assert isinstance(view, View)
        assert isinstance(view.is_photo, bool)
        assert isinstance(view.type, Type)
