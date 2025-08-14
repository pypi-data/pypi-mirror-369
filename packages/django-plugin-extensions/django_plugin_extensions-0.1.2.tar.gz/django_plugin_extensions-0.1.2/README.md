# django-plugin-extensions

[![PyPI](https://img.shields.io/pypi/v/django-plugin-extensions.svg)](https://pypi.org/project/django-plugin-extensions/)
[![Changelog](https://img.shields.io/github/v/release/Sleppy-Technologies/django-plugin-extensions?include_prereleases&label=changelog)](https://github.com/Sleppy-Technologies/django-plugin-extensions/releases)
[![Tests](https://github.com/Sleppy-Technologies/django-plugin-extensions/workflows/Test/badge.svg)](https://github.com/Sleppy-Technologies/django-plugin-extensions/actions?query=workflow%3ATest)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/Sleppy-Technologies/django-plugin-extensions/blob/main/LICENSE)

Django plugin wrapping django-extensions

## Installation

First configure your Django project [to use DJP](https://djp.readthedocs.io/en/latest/installing_plugins.html).

Then install this plugin in the same environment as your Django application.

```bash
pip install django-plugin-extensions
```

## Usage

No further configuration is needed, refer to [django-extensions documentation](https://django-extensions.readthedocs.io/en/latest/index.html) to learn about your new capabilities.

## Development

Install `uv` following [`uv`'s install documentation](https://docs.astral.sh/uv/getting-started/installation/). Install [`just`](https://just.systems/man/en/introduction.html) with `uv tool install rust-just`.

### Testing

`just test`

### Linting

`just lint`
