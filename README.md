# miscutils


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
