from pathlib import Path

from hypothesis import given

from photos.camera_uploads import ProcessingJPG
from photos.camera_uploads import try_get_next_jpg
from tests.test_strategies import jpg_paths


def test_next_camera_upload_jpg() -> None:
    if (path := try_get_next_jpg()) is not None:
        assert path.suffix == ".jpg"


class TestProcessingJPG:
    @given(path=jpg_paths())
    def test_repr_html(self, path: Path) -> None:
        processing = ProcessingJPG(path)
        _ = processing._repr_html_()
