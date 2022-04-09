import datetime as dt
from pathlib import Path

from hypothesis import given
from hypothesis import reproduce_failure
from hypothesis.strategies import sampled_from

from google_photos.main import ALL_FILES
from google_photos.main import ALL_JSON_VIEWS
from google_photos.main import ALL_PATHS
from google_photos.main import ALL_PHOTO_JSON_VIEWS
from google_photos.main import ALL_VIEWS
from google_photos.main import ROOT
from google_photos.main import UTC
from google_photos.main import JsonView
from google_photos.main import JsonViewType
from google_photos.main import PhotoJsonView
from google_photos.main import View
from google_photos.main import ViewType


_ = reproduce_failure


def test_root() -> None:
    assert ROOT.is_dir()


@given(path=sampled_from(ALL_PATHS))
def test_all_paths(path: Path) -> None:
    assert len(ALL_PATHS) == 137_552
    assert isinstance(path, Path)


@given(file=sampled_from(ALL_FILES))
def test_all_files(file: Path) -> None:
    assert len(ALL_FILES) == 137_147
    assert isinstance(file, Path)
    assert file.is_file()


@given(view=sampled_from(ALL_VIEWS))
def test_all_views(view: View) -> None:
    assert len(ALL_VIEWS) == len(ALL_FILES)
    assert isinstance(view, View)
    assert isinstance(view.is_photo, bool)
    assert isinstance(view.type, ViewType)
    hash(view)


@given(json=sampled_from(ALL_JSON_VIEWS))
def test_all_json_views(json: JsonView) -> None:
    assert len(ALL_JSON_VIEWS) == 67_732
    assert isinstance(json, JsonView)
    assert isinstance(json.contents, dict)
    assert isinstance(json.type, JsonViewType)
    hash(json)


@given(json=sampled_from(ALL_PHOTO_JSON_VIEWS))
def test_all_photo_json_views(json: PhotoJsonView) -> None:
    assert len(ALL_PHOTO_JSON_VIEWS) == 67_430
    assert isinstance(json, PhotoJsonView)
    assert isinstance(json.contents, dict)
    assert isinstance(json.description, str)
    for date in [json.creation, json.photo_taken]:
        assert isinstance(date, dt.datetime)
        assert date.tzinfo is UTC
    assert isinstance(json.title, str)
    hash(json)
