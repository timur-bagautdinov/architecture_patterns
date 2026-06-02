import time
import pytest
import requests
from requests import Response

import config
from tests.types import AddStock

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import Connection, Engine, create_engine, text
from sqlalchemy.orm import Session, clear_mappers, sessionmaker
from sqlalchemy.exc import OperationalError

from adapters.orm import metadata, start_mappers


@pytest.fixture
def in_memory_db() -> Engine:
    engine = create_engine("sqlite:///:memory:")
    metadata.create_all(engine)

    return engine


@pytest.fixture
def session(in_memory_db: Engine) -> Generator[Session]:
    start_mappers()
    yield sessionmaker(bind=in_memory_db)()

    clear_mappers()


def wait_for_webapp_to_come_up() -> Response:
    deadline = time.time() + 10
    url = config.get_api_url()

    while time.time() < deadline:
        try:
            return requests.get(url)
        except ConnectionError:
            time.sleep(0.5)
    
    pytest.fail("API never came up")


def wait_for_postgres_to_come_up(engine: Engine) -> Connection:
    deadline = time.time() + 10
    while time.time() < deadline:
        try:
            return engine.connect()
        except OperationalError:
            time.sleep(0.5)
    
    pytest.fail("Postgres never came up")


@pytest.fixture(scope="session")
def postgres_db() -> Engine:
    engine = create_engine(config.get_postgres_url())
    wait_for_postgres_to_come_up(engine)
    metadata.create_all(engine)
    return engine


@pytest.fixture
def postgres_session(postgres_db: Engine) -> Generator[Session]:
    start_mappers()
    yield sessionmaker(bind=postgres_db)()
    clear_mappers()


@pytest.fixture
def add_stock_with_cleanup(
    postgres_session: Session,
    restart_api: None,
) -> Generator[AddStock]:
    batches_added = set()
    skus_added = set()

    def _add_stock(lines: list[tuple[str, str, int, str | None]]) -> None:
        url = config.get_api_url()
        for ref, sku, qty, eta in lines:
            r = requests.post(
                f"{url}/add_batch",
                json={"ref": ref, "sku": sku, "qty": qty, "eta": eta},
            )
            assert r.status_code == 201
            

            [[batch_id]] = postgres_session.execute(
                text(
                    "SELECT id FROM batches WHERE reference=:ref AND sku=:sku" 
                ),
                dict(ref=ref, sku=sku)
            )

            batches_added.add(batch_id)
            skus_added.add(sku)
        
        postgres_session.commit()
    
    yield _add_stock

    for batch_id in batches_added:
        postgres_session.execute(
            text("DELETE FROM allocations WHERE batch_id=:batch_id"),
            dict(batch_id=batch_id)
        )

        postgres_session.execute(
            text("DELETE FROM batches WHERE id=:batch_id"),
            dict(batch_id=batch_id)
        )
    
    for sku in skus_added:
        postgres_session.execute(
            text("DELETE FROM order_lines WHERE sku=:sku"),
            dict(sku=sku)
        )
    
    postgres_session.commit()


@pytest.fixture
def restart_api() -> None:
    (Path(__file__).parent.parent / "entry_points" / "flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
