from pathlib import Path

from pytest import mark

from photos.constants import PATH_CAMERA_UPLOADS
from photos.constants import PATH_DROPBOX
from photos.constants import PATH_GOOGLE_DOWNLOAD
from photos.constants import PATH_PHOTOS


@mark.parametrize(
    "path",
    [PATH_DROPBOX, PATH_CAMERA_UPLOADS, PATH_GOOGLE_DOWNLOAD, PATH_PHOTOS],
)
def test_paths(path: Path) -> None:
    assert path.exists()
