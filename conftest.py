import time
import pytest
import requests
from requests import Response

import config

from collections.abc import Generator
from pathlib import Path

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, clear_mappers, sessionmaker

from orm import metadata, start_mappers


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


@pytest.fixture
def add_stock() -> None:
    pass


@pytest.fixture
def restart_api() -> None:
    (Path(__file__).parent / "flask_app.py").touch()
    time.sleep(0.5)
    wait_for_webapp_to_come_up()
