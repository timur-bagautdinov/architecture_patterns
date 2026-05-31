# Technical Debt

## Open

- [ ] Revisit `OrderLine` persistence mapping so it can remain a true immutable Value Object without `unsafe_hash=True`.
      Current compromise: SQLAlchemy instrumentation requires mutability, so `OrderLine` uses `@dataclass(unsafe_hash=True)`.

- [ ] Revisit pytest fixtures for SQLAlchemy sessions.
      Current fixture setup is intentionally minimal while following the book; cleanup, session closing, mapper lifecycle, and SQLAlchemy 2.0 style should be reviewed later.

- [ ] Decide repository `get()` behavior when a batch is not found.
      `SQLAlchemyRepository.get()` currently exposes SQLAlchemy's `.one()` exception for missing rows; domain/application code should not depend on persistence-specific exceptions.

- [ ] Separate unit/integration tests from end-to-end API tests.
      `test_api.py` now depends on a running web app at `localhost:5005`, so the default test command should distinguish fast local tests from Docker-backed e2e checks.

- [ ] Move domain model construction out of Flask endpoints.
      `flask_app.allocate_endpoint()` currently creates `model.OrderLine` directly; later, the service layer should accept primitive request data and construct domain objects internally.

## Done

- [x] Added `Repository.list()` to the abstract repository interface.
      `services.allocate()` depends on listing batches, so `AbstractRepository` now declares the method implemented by `SQLAlchemyRepository`.
