import pytest

import model
import repository
import services

pytestmark = pytest.mark.unit


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches):
        self._batches = set(batches)
    
    def add(self, batch):
        self._batches.add(batch)
    
    def get(self, reference):
        return next(b for b in self._batches if b.reference == reference)
    
    def list(self):
        return list(self._batches)


class FakeSession:
    def commit(self):
        pass


def test_returns_allocation():
    line = model.OrderLine("o1", "LAMP", 10)
    batch = model.Batch("b1", "LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line, repo, FakeSession())

    assert result == "b1"


def test_error_for_invalid_sku():
    line = model.OrderLine("o1", "NONEXISTENTSKU", 10)
    batch = model.Batch("b1", "LAMP", 100, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSKU, match="Invalid sku NONEXISTENTSKU"):
        services.allocate(line, repo, FakeSession())
