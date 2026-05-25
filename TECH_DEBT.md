# Technical Debt

## Open

- [ ] Revisit `OrderLine` persistence mapping so it can remain a true immutable Value Object without `unsafe_hash=True`.
      Current compromise: SQLAlchemy instrumentation requires mutability, so `OrderLine` uses `@dataclass(unsafe_hash=True)`.

- [ ] Revisit pytest fixtures for SQLAlchemy sessions.
      Current fixture setup is intentionally minimal while following the book; cleanup, session closing, mapper lifecycle, and SQLAlchemy 2.0 style should be reviewed later.

## Done
