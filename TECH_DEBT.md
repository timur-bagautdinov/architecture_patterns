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
      `entry_points.flask_app.allocate_endpoint()` currently creates `model.OrderLine` directly; later, add simple request schemas/DTOs and let the service layer accept primitive request data or commands.

- [ ] Add database constraints that preserve `Batch.reference` identity.
      The domain treats `Batch.reference` as the batch identity via `Batch.__eq__()` and `Batch.__hash__()`, but `batches.reference` is currently nullable and not unique.

- [ ] Align ORM nullability with required domain fields.
      `OrderLine.orderid`, `OrderLine.sku`, and `Batch.sku` are required strings in the domain model, but the matching ORM columns allow `NULL`.

- [ ] Tighten `allocations` table constraints.
      `allocations.orderline_id` and `allocations.batch_id` should not be nullable, and the table should prevent duplicate `(orderline_id, batch_id)` pairs to match the domain's set-based allocation model.

- [ ] Avoid creating the default database engine at `unit_of_work` import time.
      `service_layer.unit_of_work.DEFAULT_SESSION_FACTORY` currently calls `create_engine(config.get_postgres_url())` at module import time; defer this or move composition closer to the entrypoint.

- [ ] Make `FakeUnitOfWork` transaction behavior observable in service tests.
      `FakeUnitOfWork.commit()` and `FakeUnitOfWork.rollback()` currently do nothing, so service-layer tests do not verify that services cross the transaction boundary.

- [ ] Replace Flask reloader timestamp mutation in e2e setup.
      `tests.conftest.restart_api()` currently touches `entry_points/flask_app.py` to trigger a reload; replace this with an explicit test-only restart or health mechanism.

## Done

- [x] Added `Repository.list()` to the abstract repository interface.
      `services.allocate()` depends on listing batches, so `AbstractRepository` now declares the method implemented by `SQLAlchemyRepository`.
