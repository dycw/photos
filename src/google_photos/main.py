from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from enum import auto
from functools import cached_property
from itertools import chain
from pathlib import Path
from re import findall
from typing import Iterator


ROOT = Path("/data/derek/Dropbox/Apps/Google Download Your Data/")


def _recursive_iterdir(path: Path) -> Iterator[Path]:
    yield path
    for p in path.iterdir():
        if p.is_dir():
            yield from _recursive_iterdir(p)
        else:
            yield p


ALL_PATHS = list(_recursive_iterdir(ROOT))
ALL_FILES = [path for path in ALL_PATHS if path.is_file()]


class Type(Enum):
    avi = auto()
    heic = auto()
    html = auto()
    jpeg = auto()
    jpg = auto()
    json = auto()
    mov = auto()
    mp4 = auto()
    png = auto()
    tgz = auto()


@dataclass
class View:
    path: Path

    def __post_init__(self) -> None:
        assert self.path.is_file()

    @cached_property
    def _path_json(self) -> Path:
        path = self.path
        return path.with_suffix("".join(chain(path.suffixes, [".json"])))

    @cached_property
    def is_photo(self) -> bool:
        return self.type in {Type.heic, Type.jpeg, Type.jpg, Type.png}

    @cached_property
    def type(self) -> Type:
        (ext,) = findall(r"^\.(\w+)$", self.path.suffix.lower())
        return Type[ext]


ALL_VIEWS = list(map(View, ALL_FILES))
