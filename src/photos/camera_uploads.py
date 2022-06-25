from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from base64 import b64encode
from collections.abc import Iterator
from dataclasses import dataclass
from dataclasses import replace
from functools import reduce
from io import BytesIO
from itertools import chain
from pathlib import Path

from IPython.core.display import HTML
from PIL.Image import Image
from PIL.Image import open as open_image
from PIL.ImageOps import contain
from pandas import DataFrame

from photos.constants import PATH_CAMERA_UPLOADS
from photos.constants import THUMBNAIL_SIZE


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
    path: Path
    transforms: list[Transform]
    proposed: Path

    # private

    def __repr__(self) -> str:
        return repr(self._get_html())

    def _repr_html_(self) -> str:
        if isinstance(output := self._get_html()._repr_html_(), str):
            return output
        raise TypeError(type(output))

    def _add_transform(self, transform: Transform, /) -> ProcessingJPG:
        return replace(
            self, transforms=list(chain(self.transforms, [transform]))
        )

    def _get_html(self) -> HTML:
        df = DataFrame(
            [['<img src="data:image/png;base64,{0:s}">'], [2]],
            index=["thumbnail", "second"],
        )
        if not isinstance(df_html := df.to_html(escape=False), str):
            raise TypeError(type(df_html))
        buffer = BytesIO()
        contain(self._get_image_transformed(), THUMBNAIL_SIZE).save(
            buffer, format="jpeg"
        )
        return HTML(df_html.format(b64encode(buffer.getvalue()).decode()))

    def _get_image_transformed(self) -> Image:
        apply = lambda acc, el: el(acc)  # type: ignore  # noqa
        return reduce(apply, self.transforms, self._get_image_raw())

    def _get_image_raw(self) -> Image:
        return open_image(self.path)

    # public

    def rotate(self, angle: int, /) -> ProcessingJPG:
        return self._add_transform(Rotate(angle))

    def rotate90(self) -> ProcessingJPG:
        return self._add_transform(Rotate90)

    def rotate180(self) -> ProcessingJPG:
        return self._add_transform(Rotate180)


@dataclass
class Transform(ABC):
    @abstractmethod
    def __call__(self, image: Image, /) -> Image:
        raise NotImplementedError


@dataclass
class Rotate(Transform):
    angle: int

    def __call__(self, image: Image, /) -> Image:
        return image.rotate(self.angle)


Rotate90 = Rotate(90)
Rotate180 = Rotate(180)
