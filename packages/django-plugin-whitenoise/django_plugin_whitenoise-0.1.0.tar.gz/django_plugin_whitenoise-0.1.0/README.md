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

The plugin sets the `WHITENOISE_ROOT` setting to `BASE_DIR / "public"` for serving files like `robots.txt` and favicons at the root of the site. The plugin sets `WHITENOISE_KEEP_ONLY_HASHED_FILES = True` to include only useful copies of the static files. Override these settings as desired after the `djp.settings(globals())` call.

No further configuration is needed, refer to [`whitenoise` documentation](https://whitenoise.readthedocs.io/en/latest/) to learn about your new capabilities.

## Development

Install `uv` following [`uv`'s install documentation](https://docs.astral.sh/uv/getting-started/installation/). Install [`just`](https://just.systems/man/en/introduction.html) with `uv tool install rust-just`.

### Testing

`just test`

### Linting

`just lint`
