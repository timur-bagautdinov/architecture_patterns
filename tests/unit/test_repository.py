from domain import model
from adapters import repository

import pytest

from sqlalchemy import text
from sqlalchemy.orm import Session

pytestmark = pytest.mark.unit


def test_repository_can_save_a_batch(session: Session) -> None:
    batch = model.Batch("batch1", "SOAPDISH", 100, eta=None)

    insert_product(session, "SOAPDISH")

    repo = repository.SQLAlchemyRepository(session)
    product = repo.get("SOAPDISH")
    assert product is not None
    product.batches.append(batch)
    session.commit()

    rows = session.execute(
        text(
            "SELECT reference, sku, _purchased_quantity, eta FROM batches"
        )
    )

    assert list(rows) == [("batch1", "SOAPDISH", 100, None)]


def insert_order_line(session: Session, orderid: str, sku: str) -> int:
    session.execute(
        text("INSERT INTO order_lines (orderid, sku, qty) "
             "VALUES (:orderid, :sku, 12)"),
        dict(orderid=orderid, sku=sku),
    )

    [[orderline_id]] = session.execute(
        text("SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid=orderid, sku=sku),
    )

    return int(orderline_id)


def insert_batch(session: Session, reference: str, sku: str) -> int:
    session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta) "
            "VALUES (:reference, :sku, 100, null)",
        ),
        dict(reference=reference, sku=sku),
    )

    [[batch_id]] = session.execute(
        text(
            "SELECT id FROM batches WHERE reference=:reference AND sku=:sku"
        ),
        dict(reference=reference, sku=sku)
    )

    return int(batch_id)


def insert_allocation(
    session: Session,
    orderline_id: int,
    batch_id: int,
) -> None:
    session.execute(
        text(
            "INSERT INTO allocations (orderline_id, batch_id) "
            "VALUES (:orderline_id, :batch_id)"
        ),
        dict(orderline_id=orderline_id, batch_id=batch_id)
    )


def insert_product(
        session: Session,
        sku: str,
        version_number: int = 1
) -> None:
    session.execute(
        text(
            "INSERT INTO products (sku, version_number) "
            "VALUES (:sku, :version_number)"
        ),
        dict(sku=sku, version_number=version_number)
    )


def test_repository_can_retrieve_a_batch_with_allocation(
    session: Session,
) -> None:
    sku = "SOFA"
    orderline_id = insert_order_line(session, "order1", sku)
    batch_id = insert_batch(session, "batch1", sku)
    insert_batch(session, "batch2", sku)
    insert_allocation(session, orderline_id, batch_id)
    insert_product(session, sku)

    repo = repository.SQLAlchemyRepository(session)
    retrieved_product = repo.get(sku)
    assert retrieved_product is not None
    assert len(retrieved_product.batches) == 2
    retrieved = next(
        batch for batch in retrieved_product.batches
        if batch.reference == "batch1"
    )

    expected = model.Batch("batch1", sku, 100, eta=None)

    assert retrieved == expected
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {model.OrderLine("order1", sku, 12)}


def test_repository_can_list_batches(session: Session) -> None:
    sku = "SOFA"
    insert_batch(session, "batch1", sku)
    insert_batch(session, "batch2", sku)
    insert_product(session, sku=sku)

    repo = repository.SQLAlchemyRepository(session)
    product = repo.get(sku=sku)
    assert product is not None
    batches = product.batches

    assert len(batches) == 2
    assert {
        (
            batch.reference,
            batch.sku,
            batch._purchased_quantity,
            batch.eta,
        )
        for batch in batches
    } == {
        ("batch1", sku, 100, None),
        ("batch2", sku, 100, None),
    }
