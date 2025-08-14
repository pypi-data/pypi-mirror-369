import djp


@djp.hookimpl
def middleware():
    return [
        djp.Position(
            "whitenoise.middleware.WhiteNoiseMiddleware",
            after="django.middleware.security.SecurityMiddleware",
        ),
    ]


@djp.hookimpl
def settings(current_settings: dict):
    # Static files but be set up to *some* directory/path
    current_settings.setdefault(
        "STATIC_ROOT",
        current_settings["BASE_DIR"] / "staticfiles",
    )
    current_settings.setdefault("STATIC_URL", "static/")

    # Use WhiteNoise to serve static files
    current_settings.setdefault(
        "STORAGES",
        {},
    ).setdefault(
        "staticfiles",
        {},
    )["BACKEND"] = "whitenoise.storage.CompressedManifestStaticFilesStorage"

    # https://whitenoise.readthedocs.io/en/latest/django.html#using-whitenoise-in-development
    # This has no effect on the WSGI server, only the runserver command, so
    # it's OK to add it unconditionally
    current_settings.setdefault(
        "INSTALLED_APPS",
        [],
    ).insert(
        0,
        "whitenoise.runserver_nostatic",
    )

    # https://whitenoise.readthedocs.io/en/latest/django.html#WHITENOISE_ROOT
    current_settings.setdefault(
        "WHITENOISE_ROOT", current_settings["BASE_DIR"] / "public"
    )

    # https://whitenoise.readthedocs.io/en/latest/django.html#WHITENOISE_KEEP_ONLY_HASHED_FILES
    current_settings.setdefault("WHITENOISE_KEEP_ONLY_HASHED_FILES", True)
