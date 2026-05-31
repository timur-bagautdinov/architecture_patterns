from datetime import date
from typing import Protocol, Optional

from domain import model

from adapters.repository import AbstractRepository


class InvalidSKU(Exception):
    pass


class Session(Protocol):
    def commit(self) -> None:
        pass


def is_valid_sku(sku: str, batches: list[model.Batch]) -> bool:
    return sku in {b.sku for b in batches}


def allocate(orderid: str, sku: str, qty: int, repo: AbstractRepository,
             session: Session) -> str:
    line = model.OrderLine(orderid, sku, qty)
    batches = repo.list()

    if not is_valid_sku(line.sku, batches):
        raise InvalidSKU(f"Invalid sku {line.sku}")
    
    batchref = model.allocate(line, batches)
    session.commit()

    return batchref


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date],
              repo: AbstractRepository, session: Session) -> None:
    repo.add(model.Batch(ref, sku, qty, eta))
    session.commit()

