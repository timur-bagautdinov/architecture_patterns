import model

from datetime import date

import pytest

from sqlalchemy import text
from sqlalchemy.orm import Session

pytestmark = pytest.mark.unit


def test_orderline_mappers_can_load_lines(session: Session) -> None:
    session.execute(
        text(
            "INSERT INTO order_lines (orderid, sku, qty) VALUES "
            '("order1", "CHAIR", 12),'
            '("order1", "TABLE", 13),'
            '("order2", "LIPSTICK", 14)'
        )
    )

    expected = [
        model.OrderLine("order1", "CHAIR", 12),
        model.OrderLine("order1", "TABLE", 13),
        model.OrderLine("order2", "LIPSTICK", 14),
    ]

    assert session.query(model.OrderLine).all() == expected


def test_orderline_mapper_can_save_lines(session: Session) -> None:
    new_line = model.OrderLine("order1", "WIDGET", 12)

    session.add(new_line)
    session.commit()

    rows = list(session.execute(
        text(
            'SELECT orderid, sku, qty FROM order_lines'
        )
    ))

    assert rows == [("order1", "WIDGET", 12)]


def test_retrieving_batches(session: Session) -> None:
    session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta) "
            'VALUES ("batch1", "sku1", 100, null)'
        )
    )

    session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta) "
            'VALUES ("batch2", "sku2", 200, "2011-04-11")'
        )
    )

    expected = [
        model.Batch("batch1", "sku1", 100, None),
        model.Batch("batch2", "sku2", 200, date(2011, 4, 11)),
    ]

    assert session.query(model.Batch).all() == expected


def test_saving_batches(session: Session) -> None:
    batch = model.Batch("batch1", "sku1", 100, None)

    session.add(batch)
    session.commit()

    rows = session.execute(
        text(
            "SELECT reference, sku, _purchased_quantity, eta FROM batches"
        )
    )

    assert list(rows) == [("batch1", "sku1", 100, None)]


def test_saving_allocations(session: Session) -> None:
    batch = model.Batch("batch1", "sku1", 100, eta=None)
    line = model.OrderLine("order1", "sku1", 10)

    batch.allocate(line)

    session.add(batch)
    session.commit()

    rows = session.execute(
        text(
            "SELECT id FROM batches"
        )
    )

    batch_id = list(rows)[0][0]

    rows = session.execute(
        text(
            "SELECT id FROM order_lines"
        )
    )
    
    line_id = list(rows)[0][0]

    rows = session.execute(
        text(
            "SELECT orderline_id, batch_id FROM allocations"
        )
    )

    assert list(rows) == [(line_id, batch_id)]


def test_retrieving_allocations(session: Session) -> None:
    session.execute(
        text(
            "INSERT INTO order_lines (orderid, sku, qty) "
            'VALUES ("order1", "sku1", 12)'
        )
    )

    [[olid]] = session.execute(
        text(
            "SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"
        ),
        dict(orderid="order1", sku="sku1")
    )

    session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta) "
            'VALUES ("batch1", "sku1", 100, null)'
        )
    )

    [[bid]] = session.execute(
        text("SELECT id FROM batches WHERE reference=:reference AND sku=:sku"),
        dict(reference="batch1", sku="sku1")
    )

    session.execute(
        text(
            "INSERT INTO allocations (orderline_id, batch_id) "
            'VALUES (:olid, :bid)'
        ),
        dict(olid=olid, bid=bid),
    )

    batch = session.query(model.Batch).one()

    assert batch._allocations == {model.OrderLine("order1", "sku1", 12)}
