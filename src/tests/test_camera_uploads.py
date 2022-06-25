from pathlib import Path

from hypothesis import given

from photos.camera_uploads import Viewer
from photos.camera_uploads import try_get_next_jpg
from tests.test_strategies import jpg_paths


def test_next_camera_upload_jpg() -> None:
    if (path := try_get_next_jpg()) is not None:
        assert path.suffix == ".jpg"


class TestViewer:
    @given(path=jpg_paths())
    def test_viewer(self, path: Path) -> None:
        _ = Viewer(path)
