# python-service-tools

Utilities for working with python services.

![PyPI - Python Version](https://img.shields.io/pypi/pyversions/python-service-tools) ![PyPI](https://img.shields.io/pypi/v/python-service-tools.svg)

## Usage

### logging_config

Default configuration for structlog. 

Configure json logging at the INFO level:
```python
from servicetools.logging_config import default_logging, LogFormat, Verbosity

default_logging(Verbosity.INFO, LogFormat.JSON)
```

Configure text logging at the DEBUG level:
```python
from servicetools.logging_config import default_logging, LogFormat, Verbosity

default_logging(Verbosity.DEBUG, LogFormat.TEXT)
```

Configure text logging at the DEBUG level and filter out external loggers:
```python
from servicetools.logging_config import default_logging, LogFormat, Verbosity

default_logging(Verbosity.DEBUG, LogFormat.TEXT, ["extern_logger_1"])
```

### Log timing information for a function

Decorator to add timing information to the logs:
```python
from servicetools.timer import timer

import structlog

@timer(structlog.get_logger(__name__))
def some_function():
    pass
```

### Create a namespace relative patch

Create namespace relative patches:
```python
import some_package.sub_package.another_package as under_test
from servicetools.testing import relative_patch_maker

patch = relative_patch_maker(under_test.__name__)

class TestStuff:
    #equivalent to @unittest.mock.patch("some_package.sub_package.another_package.something_to_patch")
    @patch("something_to_patch")
    def test_something(self, patched):
        under_test.something()
        patched.assert_called_once()

    #equivalent to @unittest.mock.patch("some_package.sub_package.another_package.something_else_to_patch")
    @patch("something_else_to_patch")
    def test_something(self, patched):
        under_test.something()
        patched.assert_called_once()
```

### Starlette Structlog middleware 

Middleware for [Starlette](https://www.starlette.io/) framework to log HTTP 
requests to structlog. Log entries will be made at the start and end of
each request. Error requests (400s and 500s) will also be logged. Any 
calls that throw exceptions will be converted 500 responses.

```python
from servicetools.middleware import StructlogRequestMiddleware
import structlog

app.add_middleware(StructlogRequestMiddleware(app, logger=structlog.get_logger(__name__)))
```

There are options to customize the logging:

```python
import logging

import structlog
from servicetools.middleware import StructlogRequestMiddleware

app.add_middleware(StructlogRequestMiddleware(
    app,
    logger=structlog.get_logger(__name__),
    log_level=logging.DEBUG,  # Log at the DEBUG level.
    ignored_status_codes={404},  # Do not log 404 errors.
))
```

## Development Guide

This project uses [poetry](https://python-poetry.org/):

```
$ pip install poetry
$ cd to/project/root
$ poetry install
```

### Testing

Testing is done via pytest.

```
$ poetry run pytest
```