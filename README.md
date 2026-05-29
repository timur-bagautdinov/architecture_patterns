# Architecture Python

Study project for "Architecture Patterns with Python".

## Run API With Docker

Build the image:

```bash
docker build -t architecture-python-api .
```

Run the container, exposing the API on localhost:5005:

```bash
docker run --rm -p 5005:80 architecture-python-api
```

Check the app:

```bash
curl http://localhost:5005/
```

Expected response:

```text
OK
```

## Run Tests

With the API container running:

```bash
.venv/bin/python -m pytest test_api.py
```

Run the full test suite:

```bash
.venv/bin/python -m pytest
```

## Type Check

```bash
.venv/bin/python -m mypy .
```
