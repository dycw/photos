import datetime as dt
from dataclasses import dataclass
from datetime import timezone
from enum import Enum
from enum import auto
from functools import cached_property
from json import loads
from pathlib import Path
from re import findall
from re import search
from typing import Any
from typing import Iterator

from more_itertools import map_except


ROOT = Path("/data/derek/Dropbox/Apps/Google Download Your Data/")
UTC = timezone.utc


def _recursive_iterdir(path: Path) -> Iterator[Path]:
    yield path
    for p in path.iterdir():
        if p.is_dir():
            yield from _recursive_iterdir(p)
        else:
            yield p


ALL_PATHS = list(_recursive_iterdir(ROOT))
ALL_FILES = [path for path in ALL_PATHS if path.is_file()]


@dataclass(frozen=True)
class View:
    path: Path

    def __post_init__(self) -> None:
        assert self.path.is_file()

    @cached_property
    def is_photo(self) -> bool:
        return self.type in {
            ViewType.heic,
            ViewType.jpeg,
            ViewType.jpg,
            ViewType.png,
        }

    @cached_property
    def json_view(self) -> JsonView:
        if self.type is ViewType.json:
            return JsonView(self.path)
        else:
            raise TypeError(f"Invalid type: {self.type}")

    @cached_property
    def type(self) -> ViewType:
        (ext,) = findall(r"^\.(\w+)$", self.path.suffix.lower())
        return ViewType[ext]


class ViewType(Enum):
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


ALL_VIEWS = list(map(View, ALL_FILES))


@dataclass(frozen=True)
class JsonView:
    path: Path

    @cached_property
    def contents(self) -> dict[str, Any]:
        with open(self.path) as file:
            return loads(file.read())

    @cached_property
    def photo(self) -> PhotoJsonView:
        if self.type is JsonViewType.photo:
            return PhotoJsonView(self.path)
        else:
            raise TypeError(f"Invalid type: {self.type}")

    @cached_property
    def type(self) -> JsonViewType:
        if search(r"^metadata(\(\d+\))?\.json$", self.path.name) and set(
            self.contents
        ) == {"albumData"}:
            return JsonViewType.album
        elif (
            search(
                r"^(print-subscriptions|shared_album_comments|"
                r"user-generated-memory-titles)\.json$",
                self.path.name,
            )
            and set(self.contents) == set()
        ):
            return JsonViewType.other
        elif (
            self.path.name == "user-generated-memory-titles.json"
            and set(self.contents) == set()
        ):
            return JsonViewType.other
        elif set(self.contents).issuperset(
            {
                "creationTime",
                "description",
                "geoData",
                "geoDataExif",
                "imageViews",
                "photoTakenTime",
                "title",
            }
        ):
            return JsonViewType.photo
        else:
            raise NotImplementedError(self)


class JsonViewType(Enum):
    album = auto()
    photo = auto()
    other = auto()


ALL_JSON_VIEWS: list[JsonView] = list(
    map_except(lambda x: x.json_view, ALL_VIEWS, TypeError)
)


@dataclass(frozen=True)
class PhotoJsonView:
    path: Path

    @cached_property
    def contents(self) -> dict[str, Any]:
        with open(self.path) as file:
            return loads(file.read())

    @cached_property
    def description(self) -> str:
        return self.contents["title"]

    @cached_property
    def creation(self) -> dt.datetime:
        return _str_to_datetime(self.contents["creationTime"]["formatted"])

    @cached_property
    def photo_taken(self) -> dt.datetime:
        return _str_to_datetime(self.contents["photoTakenTime"]["formatted"])

    @cached_property
    def title(self) -> str:
        return self.contents["title"]


def _str_to_datetime(text: str) -> dt.datetime:
    ((day, month, year, hour, minute, second),) = findall(
        r"^(\d{1,2}) ([A-Z][a-z]{2,3}) (\d{4}), (\d{2}):(\d{2}):(\d{2}) UTC$",
        text,
    )
    day, year, hour, minute, second = map(
        int, [day, year, hour, minute, second]
    )
    if month == "Sept":
        month = 9
    else:
        month = dt.datetime.strptime(month, "%b").month
    return dt.datetime(year, month, day, hour, minute, second, tzinfo=UTC)


ALL_PHOTO_JSON_VIEWS: list[PhotoJsonView] = list(
    map_except(lambda x: x.photo, ALL_JSON_VIEWS, TypeError)
)
