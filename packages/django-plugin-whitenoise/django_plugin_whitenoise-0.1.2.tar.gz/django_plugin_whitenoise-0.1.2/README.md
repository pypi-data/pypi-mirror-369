# django-plugin-whitenoise

[![PyPI](https://img.shields.io/pypi/v/django-plugin-whitenoise.svg)](https://pypi.org/project/django-plugin-whitenoise/)
[![Changelog](https://img.shields.io/github/v/release/Sleppy-Technologies/django-plugin-whitenoise?include_prereleases&label=changelog)](https://github.com/Sleppy-Technologies/django-plugin-whitenoise/releases)
[![Tests](https://github.com/Sleppy-Technologies/django-plugin-whitenoise/workflows/Test/badge.svg)](https://github.com/Sleppy-Technologies/django-plugin-whitenoise/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/Sleppy-Technologies/django-plugin-whitenoise/blob/main/LICENSE)

Django plugin wrapping whitenoise

## Installation

First configure your Django project [to use DJP](https://djp.readthedocs.io/en/latest/installing_plugins.html).

Then install this plugin in the same environment as your Django application.

```bash
pip install django-plugin-whitenoise
```

## Usage

The plugin sets defaults for the following settings if they are found to be unset. This completely configures static file handling so you should have a working static files process just by installing the plugin.

- `WHITENOISE_ROOT` defaults to `BASE_DIR / "public"`. Put files like `robots.txt` and favicons here to serve them at the root of the site.
- `WHITENOISE_KEEP_ONLY_HASHED_FILES` defaults to `True` to include only useful copies of the static files.
- `STATICFILES_DIRS` defaults to `[BASE_DIR / "static"]`.Put project-wide static files here.
- `STATIC_ROOT` and `STATIC_URL` are set to reasonable values.

Override these settings as desired after the `djp.settings(globals())` call.

No further configuration is needed, refer to [`whitenoise` documentation](https://whitenoise.readthedocs.io/en/latest/) to learn about your new capabilities.

## Development

Install `uv` following [`uv`'s install documentation](https://docs.astral.sh/uv/getting-started/installation/). Install [`just`](https://just.systems/man/en/introduction.html) with `uv tool install rust-just`.

### Testing

`just test`

### Linting

`just lint`
