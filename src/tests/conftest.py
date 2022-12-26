from hypothesis import settings


settings.register_profile(
    "default", max_examples=1000, deadline=None, print_blob=True
)
settings.load_profile("default")
