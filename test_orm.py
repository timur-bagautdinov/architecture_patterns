import model
from sqlalchemy import text
from sqlalchemy.orm import Session


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
