import pytest

from datetime import date, timedelta

from model import Batch, OrderLine, OutOfStock, allocate

pytestmark = pytest.mark.unit

today = date.today()
tomorrow = today + timedelta(days=1)
later = today + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipment() -> None:
    in_stock_batch = Batch("in-stock-batch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tomorrow)

    line = OrderLine('oref', "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_allocate_earlier_batches() -> None:
    earliest = Batch("speedy-batch", "SPOON", 100, eta=today)
    medium = Batch("normal-batch", "SPOON", 100, eta=tomorrow)
    latest = Batch("slow-batch", "SPOON", 100, eta=later)

    line = OrderLine("order1", "SPOON", 10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_skips_earlier_batches_with_not_enough_available_quantity() -> None:
    too_small_batch = Batch("too-small-batch", "LAMP", 5, eta=today)
    enough_batch = Batch("enough-batch", "LAMP", 100, eta=tomorrow)

    line = OrderLine("order1", "LAMP", 10)

    allocate(line, [enough_batch, too_small_batch])

    assert too_small_batch.available_quantity == 5
    assert enough_batch.available_quantity == 90


def test_returns_allocated_batch_ref() -> None:
    in_stock_batch = Batch("in-stock-batch-ref", "POSTER", 100, eta=None)
    shipment_batch = Batch("shipment-batch-ref", "POSTER", 100, eta=tomorrow)

    line = OrderLine("oref", "POSTER", 10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raise_out_of_stock_exception_if_cannot_allocate() -> None:
    batch = Batch("batch1", "FORK", 10, eta=today)

    allocate(OrderLine("order1", "FORK", 10), [batch])

    with pytest.raises(OutOfStock, match="FORK"):
        allocate(OrderLine("order2", "FORK", 1), [batch])
