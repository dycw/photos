from __future__ import annotations

from google_photos.main import ALL_EXTS
from google_photos.main import ALL_FILES
from google_photos.main import ALL_PATHS
from google_photos.main import ROOT
from google_photos.main import get_extension


def test_root() -> None:
    assert ROOT.is_dir()


def test_all_paths() -> None:
    assert len(ALL_PATHS) == 137552


def test_all_files() -> None:
    assert len(ALL_FILES) == 137147


def test_all_suffixes() -> None:
    assert ALL_EXTS == {
        ".HEIC",
        ".JPG",
        ".MOV",
        ".MP4",
        ".PNG",
        ".avi",
        ".heic",
        ".html",
        ".jpeg",
        ".jpg",
        ".json",
        ".mov",
        ".mp4",
        ".png",
        ".tgz",
    }


def test_get_extension() -> None:
    for file in ALL_FILES:
        get_extension(file)
