# miscutils

Utilities for working with python projects.

## Usage

### logging_config

Default configuration for structlog. 

Configure json logging at the INFO level:
```python
from miscutils.logging_config import default_logging, LogFormat, Verbosity

default_logging(Verbosity.INFO, LogFormat.JSON)
```

Configure text logging at the DEBUG level:
```python
from miscutils.logging_config import default_logging, LogFormat, Verbosity

default_logging(Verbosity.DEBUG, LogFormat.TEXT)
```

Configure text logging at the DEBUG level and filter out external loggers:
```python
from miscutils.logging_config import default_logging, LogFormat, Verbosity

default_logging(Verbosity.DEBUG, LogFormat.TEXT, ["extern_logger_1"])
```

### Log timing information for a function

Decorator to add timing information to the logs:
```python
from miscutils.timer import timer

import structlog

@timer(structlog.get_logger(__name__))
def some_function():
    pass
```

## Testing

Testing is done via pytest.

```
$ pip install -r requirements.txt
$ pytest
```

To get code coverage information, you can run pytest directly.

```
$ pip install -r requirements.txt
$ pytest --cov=src --cov-report=html
```

This will generate an html coverage report in `htmlcov/` directory.
