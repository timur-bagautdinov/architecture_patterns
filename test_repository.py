import model
import repository

from sqlalchemy import text
from sqlalchemy.orm import Session


def test_repository_can_save_a_batch(session: Session) -> None:
    batch = model.Batch("batch1", "SOAPDISH", 100, eta=None)

    repo = repository.SQLAlchemyRepository(session)
    repo.add(batch)
    session.commit()

    rows = session.execute(
        text(
            "SELECT reference, sku, _purchased_quantity, eta FROM batches"
        )
    )

    assert list(rows) == [("batch1", "SOAPDISH", 100, None)]


def insert_order_line(session: Session, orderid: str) -> int:
    session.execute(
        text("INSERT INTO order_lines (orderid, sku, qty) "
             'VALUES (:orderid, "SOFA", 12)'),
        dict(orderid=orderid),
    )

    [[orderline_id]] = session.execute(
        text("SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid=orderid, sku="SOFA"),
    )

    return int(orderline_id)


def insert_batch(session: Session, reference: str) -> int:
    session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta) "
            'VALUES (:reference, "SOFA", 100, null)',
        ),
        dict(reference=reference),
    )

    [[batch_id]] = session.execute(
        text(
            "SELECT id FROM batches WHERE reference=:reference AND sku=:sku"
        ),
        dict(reference=reference, sku="SOFA")
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


def test_repository_can_retrieve_a_batch_with_allocation(
    session: Session,
) -> None:
    orderline_id = insert_order_line(session, "order1")
    batch_id = insert_batch(session, "batch1")
    insert_batch(session, "batch2")
    insert_allocation(session, orderline_id, batch_id)

    repo = repository.SQLAlchemyRepository(session)
    retrieved = repo.get("batch1")

    expected = model.Batch("batch1", "SOFA", 100, eta=None)

    assert retrieved == expected
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {model.OrderLine("order1", "SOFA", 12)}


def test_repository_can_list_batches(session: Session) -> None:
    insert_batch(session, "batch1")
    insert_batch(session, "batch2")

    repo = repository.SQLAlchemyRepository(session)
    batches = repo.list()

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
        ("batch1", "SOFA", 100, None),
        ("batch2", "SOFA", 100, None),
    }
