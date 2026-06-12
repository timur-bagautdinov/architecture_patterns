from datetime import date
from typing import Optional

from domain import model

from service_layer import unit_of_work


class InvalidSKU(Exception):
    pass


def allocate(orderid: str, sku: str, qty: int, 
             uow: unit_of_work.AbstractUnitOfWork) -> str:
    line = model.OrderLine(orderid, sku, qty)
    with uow:
        product = uow.products.get(line.sku)

        if product is None:
            raise InvalidSKU(f"Invalid sku {line.sku}")
        
        batchref = product.allocate(line)
        uow.commit()

    return batchref


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date],
              uow: unit_of_work.AbstractUnitOfWork) -> None:
    with uow:
        product = uow.products.get(sku)
        if product is None:
            product = model.Product(sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(ref, sku, qty, eta))
        uow.commit()
