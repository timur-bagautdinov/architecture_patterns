from typing import Protocol

from domain import model

from adapters.repository import AbstractRepository


class InvalidSKU(Exception):
    pass


class Session(Protocol):
    def commit(self) -> None:
        pass


def is_valid_sku(sku: str, batches: list[model.Batch]) -> bool:
    return sku in {b.sku for b in batches}


def allocate(line: model.OrderLine, repo: AbstractRepository, session: Session) -> str:
    batches = repo.list()

    if not is_valid_sku(line.sku, batches):
        raise InvalidSKU(f"Invalid sku {line.sku}")
    
    batchref = model.allocate(line, batches)
    session.commit()

    return batchref
