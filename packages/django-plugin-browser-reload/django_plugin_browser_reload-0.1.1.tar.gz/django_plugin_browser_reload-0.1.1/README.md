# django-plugin-browser-reload

[![PyPI](https://img.shields.io/pypi/v/django-plugin-browser-reload.svg)](https://pypi.org/project/django-plugin-browser-reload/)
[![Changelog](https://img.shields.io/github/v/release/Sleppy-Technologies/django-plugin-browser-reload?include_prereleases&label=changelog)](https://github.com/Sleppy-Technologies/django-plugin-browser-reload/releases)
[![Tests](https://github.com/Sleppy-Technologies/django-plugin-browser-reload/workflows/Test/badge.svg)](https://github.com/Sleppy-Technologies/django-plugin-browser-reload/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/Sleppy-Technologies/django-plugin-browser-reload/blob/main/LICENSE)

Django plugin wrapping django-browser-reload

## Installation

First configure your Django project [to use DJP](https://djp.readthedocs.io/en/latest/installing_plugins.html).

Then install this plugin in the same environment as your Django application.

```bash
pip install django-plugin-browser-reload
```

## Usage

This package alters the responses only when `DEBUG = True`.

No further configuration is needed, refer to [`django-browser-reload` documentation](https://github.com/adamchainz/django-browser-reload) to learn about your new capabilities.

## Development

Install `uv` following [`uv`'s install documentation](https://docs.astral.sh/uv/getting-started/installation/). Install [`just`](https://just.systems/man/en/introduction.html) with `uv tool install rust-just`.

### Testing

`just test`

### Linting

`just lint`
