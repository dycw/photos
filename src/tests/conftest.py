from hypothesis import settings


settings.register_profile(
    "default", deadline=None, max_examples=1000, print_blob=True
)
settings.load_profile("default")
