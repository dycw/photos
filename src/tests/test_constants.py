from pathlib import Path

from pytest import mark

from photos.constants import (
    PATH_CAMERA_UPLOADS,
    PATH_DROPBOX,
    PATH_GOOGLE_DOWNLOAD,
    PATH_MONTHLY,
    PATH_PHOTOS,
)


@mark.parametrize(
    "path",
    [
        PATH_DROPBOX,
        PATH_CAMERA_UPLOADS,
        PATH_GOOGLE_DOWNLOAD,
        PATH_PHOTOS,
        PATH_MONTHLY,
    ],
)
def test_paths(path: Path) -> None:
    assert path.exists()
