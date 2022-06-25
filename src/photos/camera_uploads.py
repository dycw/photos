from __future__ import annotations

from base64 import b64encode
from collections.abc import Iterator
from dataclasses import dataclass
from dataclasses import field
from dataclasses import replace
from functools import reduce
from io import BytesIO
from itertools import chain
from pathlib import Path
from shutil import copy
from shutil import move
from typing import Any

from IPython.core.display import HTML
from PIL.Image import Image
from PIL.Image import open as open_image
from PIL.ImageOps import contain
from dycw_utilities.pathlib import PathLike
from humanize import naturalsize
from loguru import logger
from pandas import DataFrame

from photos.constants import PATH_CAMERA_UPLOADS
from photos.constants import PATH_MONTHLY
from photos.constants import THUMBNAIL_SIZE
from photos.transforms import Rotate
from photos.transforms import Rotate90
from photos.transforms import Rotate180
from photos.transforms import Transform
from photos.utilities import get_datetime
from photos.utilities import get_destination
from photos.utilities import get_file_size
from photos.utilities import get_parsed_exif_tags
from photos.utilities import get_resolution


def yield_camera_upload_jpgs() -> Iterator[Path]:
    while (path := try_get_next_jpg()) is not None:
        _ = process_jpg(path)


def try_get_next_jpg() -> Path | None:
    it = (
        path
        for path in sorted(PATH_CAMERA_UPLOADS.iterdir())
        if path.as_posix().endswith(".jpg")
    )
    return next(it, None)


@dataclass(repr=False)
class ProcessingJPG:
    """Class for processing a JPG."""

    path: PathLike
    transforms: list[Transform] = field(default_factory=list)

    # private

    def __post_init__(self) -> None:
        self._file_size = get_file_size(self.path)
        self._datetime = get_datetime(image := self._open_image())
        self._resolution = get_resolution(image)
        self._tags = get_parsed_exif_tags(image)

    def __repr__(self) -> str:
        return repr(self._get_html())

    def _add_transform(self, transform: Transform, /) -> ProcessingJPG:
        return replace(
            self, transforms=list(chain(self.transforms, [transform]))
        )

    def _get_destination(self, *, root: PathLike = PATH_MONTHLY) -> Path | None:
        if (datetime := self._datetime) is None:
            return None
        else:
            return get_destination(datetime, root=root, suffix=".jpg")

    def _get_final_image(self) -> Image:
        apply = lambda acc, el: el(acc)  # type: ignore  # noqa
        return reduce(apply, self.transforms, self._open_image())

    def _get_html(self) -> HTML:
        index, values = zip(*self._yield_html_elements())
        df = DataFrame(values, index=index)
        if not isinstance(html := df.to_html(escape=False), str):
            raise TypeError(type(html))
        self._get_thumbnail().save(buffer := BytesIO(), format="jpeg")
        return HTML(html.format(b64encode(buffer.getvalue()).decode()))

    def _get_thumbnail(self) -> Image:
        return contain(self.rotate180()._get_final_image(), THUMBNAIL_SIZE)

    def _open_image(self) -> Image:
        return open_image(self.path)

    def _repr_html_(self) -> str:
        if isinstance(output := self._get_html()._repr_html_(), str):
            return output
        raise TypeError(type(output))

    def _yield_html_elements(self) -> Iterator[tuple[str, Any]]:
        yield "thumbnail", '<img src="data:image/png;base64,{0:s}">'
        yield "path", self.path
        yield "file size", naturalsize(self._file_size)
        yield "datetime", self._datetime
        yield "resolution", self._resolution
        yield "destination", self._get_destination()

    # public

    def rotate(self, angle: int, /) -> ProcessingJPG:
        return self._add_transform(Rotate(angle))

    def rotate90(self) -> ProcessingJPG:
        return self._add_transform(Rotate90)

    def rotate180(self) -> ProcessingJPG:
        return self._add_transform(Rotate180)

    def copy(self, path: PathLike | None = None, /) -> None:
        dest = self._get_destination() if path is None else path
        if dest is None:
            raise ValueError(f"{dest=}")
        copy(src := self.path, dest)
        logger.info("Copied:\n    {}\n--> {}", src, dest)

    def move(self, path: PathLike | None = None, /) -> None:
        dest = self._get_destination() if path is None else path
        if dest is None:
            raise ValueError(f"{dest=}")
        move(src := self.path, dest)
        logger.info("Moved:\n    {}\n--> {}", src, dest)
