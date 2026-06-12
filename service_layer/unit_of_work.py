from __future__ import annotations

import abc
from collections.abc import Callable
from types import TracebackType

import config

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from adapters import repository


DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        config.get_postgres_url()
    )
)


class AbstractUnitOfWork(abc.ABC):
    products: repository.AbstractRepository

    def __enter__(self) -> AbstractUnitOfWork:
        return self
    
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        self.rollback()
    
    @abc.abstractmethod
    def commit(self) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def rollback(self) -> None:
        raise NotImplementedError


class SQLAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        session_factory: Callable[[], Session] = DEFAULT_SESSION_FACTORY,
    ) -> None:
        self.session_factory = session_factory
    
    def __enter__(self) -> AbstractUnitOfWork:
        self.session = self.session_factory()
        self.products = repository.SQLAlchemyRepository(self.session)
        return super().__enter__()
    
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        super().__exit__(exc_type, exc, tb)
        self.session.close()
    
    def commit(self) -> None:
        self.session.commit()
    
    def rollback(self) -> None:
        self.session.rollback()
