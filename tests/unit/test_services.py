import pytest

from domain import model
from adapters import repository
from service_layer import services, unit_of_work

pytestmark = pytest.mark.unit


class FakeRepository(repository.AbstractRepository):
    def __init__(self, products: list[model.Product] | None = None) -> None:
        self._products = set(products or [])
    
    def add(self, product: model.Product) -> None:
        self._products.add(product)
    
    def get(self, sku: str) -> model.Product | None:
        return next((p for p in self._products if p.sku == sku), None)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self) -> None:
        self.products = FakeRepository()
    
    def commit(self) -> None:
        pass

    def rollback(self) -> None:
        pass


def test_returns_allocation() -> None:
    uow = FakeUnitOfWork()
    services.add_batch("b1", "LAMP", 100, None, uow)

    result = services.allocate("o1", "LAMP", 10, uow)

    assert result == "b1"

def test_error_for_invalid_sku() -> None:
    uow = FakeUnitOfWork()
    services.add_batch("b1", "LAMP", 100, None, uow)

    with pytest.raises(services.InvalidSKU, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, uow)


def test_add_batch() -> None:
    uow = FakeUnitOfWork()

    services.add_batch("b1", "LAMP", 100, None, uow)

    assert uow.products.get("LAMP") is not None
