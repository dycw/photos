from pathlib import Path


PATH_DROPBOX = Path("/data/derek/Dropbox")
PATH_CAMERA_UPLOADS = PATH_DROPBOX.joinpath("Camera Uploads")
PATH_GOOGLE_DOWNLOAD = PATH_DROPBOX.joinpath(
    "Apps", "Google Download Your Data"
)
PATH_PHOTOS = PATH_DROPBOX.joinpath("Photos")


THUMBNAIL_SIZE = (600, 600)
