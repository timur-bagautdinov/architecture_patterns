import pytest

from datetime import date
from sqlalchemy import text
from sqlalchemy.orm import Session, sessionmaker

from domain import model
from service_layer import unit_of_work


pytestmark = pytest.mark.integration


def insert_batch(session: Session, ref: str, sku: str, qty: int, eta: date | None,
                 product_version: int = 1) -> None:
    session.execute(
        text(
            "INSERT INTO products (sku, version_number) "
            "VALUES(:sku, :version)"
        ),
        dict(sku=sku, version=product_version)
    )
    
    session.execute(
        text(
            "INSERT INTO batches (reference, sku, _purchased_quantity, eta) "
            "VALUES (:ref, :sku, :qty, :eta)"
        ),
        dict(ref=ref, sku=sku, qty=qty, eta=eta)
    )


def get_allocated_batch_ref(session: Session, orderid: str, sku: str) -> str:
    [[orderlineid]] = session.execute(
        text("SELECT id FROM order_lines WHERE orderid=:orderid AND sku=:sku"),
        dict(orderid=orderid, sku=sku)
    )

    batchref: str
    [[batchref]] = session.execute(
        text("SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id "
             "WHERE orderline_id=:orderlineid"),
        dict(orderlineid=orderlineid)
    )

    return batchref


def test_uow_can_retrieve_a_batch_and_allocate_to_it(
    session_factory: sessionmaker[Session],
) -> None:
    session = session_factory()
    insert_batch(session, "batch1", "BENCH", 100, None)
    session.commit()

    uow = unit_of_work.SQLAlchemyUnitOfWork(session_factory)
    with uow:
        product = uow.products.get("BENCH")
        assert product is not None
        line = model.OrderLine("o1", "BENCH", 10)
        product.allocate(line)
        uow.commit()
    
    batchref = get_allocated_batch_ref(session, "o1", "BENCH")
    assert batchref == "batch1"


def test_rolls_back_uncommited_work_by_default(
    session_factory: sessionmaker[Session],
) -> None:
    uow = unit_of_work.SQLAlchemyUnitOfWork(session_factory)

    with uow:
        insert_batch(uow.session, "batch1", "BENCH", 100, None)
    
    new_session = session_factory()
    rows = list(new_session.execute(text("SELECT * FROM batches")))

    assert rows == []


def test_rolls_back_on_error(session_factory: sessionmaker[Session]) -> None:
    class TestException(Exception):
        pass

    uow = unit_of_work.SQLAlchemyUnitOfWork(session_factory)
    with pytest.raises(TestException):
        with uow:
            insert_batch(uow.session, "batch1", "BENCH", 100, None)
            # immitate the error
            raise TestException()
    
    new_session = session_factory()
    rows = list(new_session.execute(text("SELECT * FROM batches")))

    assert rows == []
