import pytest

from domain import model
from adapters import repository
from service_layer import services, unit_of_work

pytestmark = pytest.mark.unit


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches: list[model.Batch] | None = None) -> None:
        self._batches = set(batches or [])
    
    def add(self, batch: model.Batch) -> None:
        self._batches.add(batch)
    
    def get(self, reference: str) -> model.Batch:
        return next(b for b in self._batches if b.reference == reference)
    
    def list(self) -> list[model.Batch]:
        return list(self._batches)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self) -> None:
        self.batches = FakeRepository()
    
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

    assert uow.batches.get("b1") is not None
