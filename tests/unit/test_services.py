import pytest

from domain import model
from adapters import repository
from service_layer import services

pytestmark = pytest.mark.unit


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches: list[model.Batch]) -> None:
        self._batches = set(batches)
    
    def add(self, batch: model.Batch) -> None:
        self._batches.add(batch)
    
    def get(self, reference: str) -> model.Batch:
        return next(b for b in self._batches if b.reference == reference)
    
    def list(self) -> list[model.Batch]:
        return list(self._batches)


class FakeSession:
    def commit(self) -> None:
        pass


def test_returns_allocation() -> None:
    batch = model.Batch("b1", "LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate("o1", "LAMP", 10, repo, FakeSession())

    assert result == "b1"


def test_error_for_invalid_sku() -> None:
    batch = model.Batch("b1", "LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSKU, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, FakeSession())
