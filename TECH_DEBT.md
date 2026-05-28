# Technical Debt

## Open

- [ ] Revisit `OrderLine` persistence mapping so it can remain a true immutable Value Object without `unsafe_hash=True`.
      Current compromise: SQLAlchemy instrumentation requires mutability, so `OrderLine` uses `@dataclass(unsafe_hash=True)`.

- [ ] Revisit pytest fixtures for SQLAlchemy sessions.
      Current fixture setup is intentionally minimal while following the book; cleanup, session closing, mapper lifecycle, and SQLAlchemy 2.0 style should be reviewed later.

- [ ] Decide whether `Repository.list()` belongs in the abstract repository interface.
      `SQLAlchemyRepository` currently exposes `list()`, but `AbstractRepository` only declares `add()` and `get()`.

- [ ] Decide repository `get()` behavior when a batch is not found.
      `SQLAlchemyRepository.get()` currently exposes SQLAlchemy's `.one()` exception for missing rows; domain/application code should not depend on persistence-specific exceptions.

## Done
