# Architecture Python

Study project for "Architecture Patterns with Python".

## Run API and Postgres With Docker Compose

Start the Flask app and Postgres:

```bash
docker compose up --build
```

Or run them in the background:

```bash
docker compose up --build -d
```

Check the app:

```bash
curl http://localhost:5005/
```

Expected response:

```text
OK
```

The API is exposed on `localhost:5005`.
Postgres is exposed on `localhost:54321`.

View logs:

```bash
docker compose logs -f
```

Stop the containers:

```bash
docker compose down
```

Stop the containers and remove the Postgres data volume:

```bash
docker compose down -v
```

## Run Tests

Run tests that do not require Docker containers:

```bash
make unit
```

With the Docker Compose stack running, run end-to-end tests:

```bash
make e2e
```

Run the full test suite:

```bash
make test
```

## Type Check

```bash
.venv/bin/python -m mypy .
```
