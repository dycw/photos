from datetime import timezone
from pathlib import Path


ROOT = Path("/data/derek/Dropbox/Apps/Google Download Your Data/")
UTC = timezone.utc


# @dataclass(frozen=True)
# class JsonView:
#     path: Path

#     @cached_property
#     def contents(self) -> dict[str, Any]:
#         with open(self.path) as file:
#             return loads(file.read())

#     @cached_property
#     def photo(self) -> PhotoJsonView:
#         if self.type is JsonViewType.photo:
#             return PhotoJsonView(self.path)
#         else:
#             raise TypeError(f"Invalid type: {self.type}")

#     @cached_property
#     def type(self) -> JsonViewType:
#         if search(r"^metadata(\(\d+\))?\.json$", self.path.name) and set(
#             self.contents
#         ) == {"albumData"}:
#             return JsonViewType.album
#         elif (
#             search(
#                 r"^(print-subscriptions|shared_album_comments|"
#                 r"user-generated-memory-titles)\.json$",
#                 self.path.name,
#             )
#             and set(self.contents) == set()
#         ):
#             return JsonViewType.other
#         elif (
#             self.path.name == "user-generated-memory-titles.json"
#             and set(self.contents) == set()
#         ):
#             return JsonViewType.other
#         elif set(self.contents).issuperset(
#             {
#                 "creationTime",
#                 "description",
#                 "geoData",
#                 "geoDataExif",
#                 "imageViews",
#                 "photoTakenTime",
#                 "title",
#             }
#         ):
#             return JsonViewType.photo
#         else:
#             raise NotImplementedError(self)


# class JsonViewType(Enum):
#     album = auto()
#     photo = auto()
#     other = auto()


# ALL_JSON_VIEWS: list[JsonView] = list(
#     map_except(lambda x: x.json_view, ALL_VIEWS, TypeError)
# )


# @dataclass(frozen=True)
# class PhotoJsonView:
#     path: Path

#     @cached_property
#     def contents(self) -> dict[str, Any]:
#         with open(self.path) as file:
#             return loads(file.read())

#     @cached_property
#     def description(self) -> str:
#         return self.contents["title"]

#     @cached_property
#     def creation(self) -> dt.datetime:
#         return _str_to_datetime(self.contents["creationTime"]["formatted"])

#     @cached_property
#     def photo_taken(self) -> dt.datetime:
#         return _str_to_datetime(self.contents["photoTakenTime"]["formatted"])

#     @cached_property
#     def title(self) -> str:
#         return self.contents["title"]


# def _str_to_datetime(text: str) -> dt.datetime:
#     ((day, month, year, hour, minute, second),) = findall(
#         r"^(\d{1,2}) ([A-Z][a-z]{2,3}) (\d{4}), (\d{2}):(\d{2}):(\d{2}) UTC$",
#         text,
#     )
#     day, year, hour, minute, second = map(
#         int, [day, year, hour, minute, second]
#     )
#     if month == "Sept":
#         month = 9
#     else:
#         month = dt.datetime.strptime(month, "%b").month
#     return dt.datetime(year, month, day, hour, minute, second, tzinfo=UTC)


# ALL_PHOTO_JSON_VIEWS: list[PhotoJsonView] = list(
#     map_except(lambda x: x.photo, ALL_JSON_VIEWS, TypeError)
# )
