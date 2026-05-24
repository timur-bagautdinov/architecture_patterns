from datetime import date

from model import Batch, OrderLine


def make_batch_and_line(sku: str, batch_qty: int, line_qty: int) -> tuple[Batch, OrderLine]:
    return (Batch("batch-001", sku, batch_qty, eta=date.today()),
            OrderLine("order-123", sku, line_qty))


def test_allocating_to_a_batch_reduces_the_available_quantity() -> None:
    batch = Batch("batch-01", "SMALL-TABLE", qty=20, eta=date.today())

    line = OrderLine("order-ref", "SMALL-TABLE", 2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required() -> None:
    large_batch, small_line = make_batch_and_line("ELEGANT-LAMP", 20, 2)

    assert large_batch.can_allocate(small_line)


def test_cannot_allocate_if_available_smaller_than_required() -> None:
    small_batch, large_line = make_batch_and_line("ELEGANT-LAMP", 2, 20)

    assert small_batch.can_allocate(large_line) is False


def test_can_allocate_if_available_equal_to_required() -> None:
    batch, line = make_batch_and_line("ELEGANT-LAMP", 2, 2)

    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_not_match() -> None:
    batch = Batch("batch-001", "CHAIR", 100, eta=None)
    different_sku_line = OrderLine("order-123", "TOASTER", 10)

    assert batch.can_allocate(different_sku_line) is False


def test_can_only_deallocate_allocated_lines() -> None:
    batch, unallocated_line = make_batch_and_line("TRINKET", 20, 2)

    batch.deallocate(unallocated_line)

    assert batch.available_quantity == 20


def test_allocation_is_idempotent() -> None:
    batch, line = make_batch_and_line("ANGULAR-DESK", 20, 2)
    batch.allocate(line)
    batch.allocate(line)

    assert batch.available_quantity == 18


def test_can_allocate_multiple_order_lines() -> None:
    batch = Batch("batch-001", "TABLE", 20, eta=None)

    line_1 = OrderLine("order-001", "TABLE", 2)
    line_2 = OrderLine("order-002", "TABLE", 3)

    batch.allocate(line_1)
    batch.allocate(line_2)

    assert batch.available_quantity == 15


def test_cannot_allocate_second_line_if_not_enough_available_quantity() -> None:
    batch = Batch("batch-001", "TABLE", 3, eta=None)

    line_1 = OrderLine("order-001", "TABLE", 2)
    line_2 = OrderLine("order-002", "TABLE", 2)

    assert batch.can_allocate(line_1)

    batch.allocate(line_1)

    assert batch.can_allocate(line_2) is False

    batch.allocate(line_2)

    assert batch.available_quantity == 1
