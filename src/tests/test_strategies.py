from pathlib import Path

from PIL.Image import Image
from hypothesis import given
from hypothesis.strategies import SearchStrategy
from hypothesis.strategies import sampled_from

from photos.constants import PATH_CAMERA_UPLOADS
from photos.utilities import is_jpg
from photos.utilities import open_image


def jpg_paths() -> SearchStrategy[Path]:
    return sampled_from(sorted(filter(is_jpg, PATH_CAMERA_UPLOADS.iterdir())))


@given(path=jpg_paths())
def test_jpg_paths(path: Path) -> None:
    assert isinstance(path, Path)
    assert is_jpg(path)
    assert path.relative_to(PATH_CAMERA_UPLOADS)


def jpg_images() -> SearchStrategy[Image]:
    return jpg_paths().map(open_image)


@given(image=jpg_images())
def test_jpg_images(image: Image) -> None:
    assert isinstance(image, Image)
