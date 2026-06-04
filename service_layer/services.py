from datetime import date
from typing import Protocol, Optional

from domain import model

from adapters.repository import AbstractRepository
from service_layer import unit_of_work


class InvalidSKU(Exception):
    pass


class Session(Protocol):
    def commit(self) -> None:
        pass


def is_valid_sku(sku: str, batches: list[model.Batch]) -> bool:
    return sku in {b.sku for b in batches}


def allocate(orderid: str, sku: str, qty: int, 
             uow: unit_of_work.AbstractUnitOfWork) -> str:
    line = model.OrderLine(orderid, sku, qty)
    with uow:
        batches = uow.batches.list()

        if not is_valid_sku(line.sku, batches):
            raise InvalidSKU(f"Invalid sku {line.sku}")
        
        batchref = model.allocate(line, batches)
        uow.commit()

    return batchref


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date],
              uow: unit_of_work.AbstractUnitOfWork) -> None:
    with uow:
        uow.batches.add(model.Batch(ref, sku, qty, eta))
        uow.commit()
