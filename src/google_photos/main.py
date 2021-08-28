from __future__ import annotations

from enum import Enum
from enum import auto
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
ALL_EXTS = {file.suffix for file in ALL_FILES}


class Extension(Enum):
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


def get_extension(path: Path) -> Extension:
    (ext,) = findall(r"^\.(\w+)$", path.suffix.lower())
    return Extension[ext]
