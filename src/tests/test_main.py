from __future__ import annotations

from pathlib import Path

from hypothesis import given
from hypothesis import reproduce_failure
from hypothesis.strategies import sampled_from

from google_photos.main import ALL_FILES
from google_photos.main import ALL_JSON_VIEWS
from google_photos.main import ALL_PATHS
from google_photos.main import ALL_VIEWS
from google_photos.main import ROOT
from google_photos.main import JsonView
from google_photos.main import Type
from google_photos.main import View


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
def test_st_views(view: View) -> None:
    assert len(ALL_VIEWS) == len(ALL_FILES)
    assert isinstance(view, View)
    assert isinstance(view.is_photo, bool)
    assert isinstance(view.type, Type)
    assert isinstance(hash(view), int)


@given(json=sampled_from(ALL_JSON_VIEWS))
def test_st_json(json: JsonView) -> None:
    assert len(ALL_JSON_VIEWS) == 67_732
    assert isinstance(json, JsonView)
    assert json.type is Type.json
    assert isinstance(json.contents, dict)
    assert isinstance(json.title, str)
    assert isinstance(hash(json), int)
    # we could foo = one(view for view in ALL_VIEWS if view.path.name == json.title)
