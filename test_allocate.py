from datetime import date, timedelta

from model import Batch, OrderLine, allocate

today = date.today()
tommorow = today + timedelta(days=1)


def test_prefers_current_stock_batches_to_shipment() -> None:
    in_stock_batch = Batch("in-stock-bactch", "RETRO-CLOCK", 100, eta=None)
    shipment_batch = Batch("shipment-batch", "RETRO-CLOCK", 100, eta=tommorow)

    line = OrderLine('oref', "RETRO-CLOCK", 10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100
