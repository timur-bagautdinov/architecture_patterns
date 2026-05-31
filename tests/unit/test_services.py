import pytest

from domain import model
from adapters import repository
from service_layer import services

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


class FakeSession:
    def commit(self) -> None:
        pass


def test_returns_allocation() -> None:
    repo = FakeRepository()
    session = FakeSession()
    services.add_batch("b1", "LAMP", 100, None, repo, session)

    result = services.allocate("o1", "LAMP", 10, repo, session)

    assert result == "b1"


def test_error_for_invalid_sku() -> None:
    repo = FakeRepository()
    session = FakeSession()
    services.add_batch("b1", "LAMP", 100, None, repo, session)

    with pytest.raises(services.InvalidSKU, match="Invalid sku NONEXISTENTSKU"):
        services.allocate("o1", "NONEXISTENTSKU", 10, repo, session)


def test_add_batch() -> None:
    repo = FakeRepository()

    services.add_batch("b1", "LAMP", 100, None, repo, FakeSession())

    assert repo.get("b1") is not None
