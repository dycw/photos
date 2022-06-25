from hypothesis import settings


settings.register_profile("default", deadline=None, print_blob=True)
settings.load_profile("default")
