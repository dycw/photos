from photos.camera_uploads import try_get_next_jpg


def test_next_camera_upload_jpg() -> None:
    if (path := try_get_next_jpg()) is not None:
        assert path.suffix == ".jpg"
