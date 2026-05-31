import uuid
import pytest
import requests

import config

pytestmark = pytest.mark.e2e


def random_suffix() -> str:
    return uuid.uuid4().hex[:6]


def random_sku(name: str = "") -> str:
    return f"sku-{name}-{random_suffix()}"


def random_batchref(name:str = "") -> str:
    return f"batch-{name}-{random_suffix()}"


def random_orderid(name:str = "") -> str:
    return f"order-{name}-{random_suffix()}"


@pytest.mark.usefixtures("restart_api")
def test_happy_path_returns_201_and_allocated_batch(add_stock_with_cleanup: None) -> None:
    sku = random_sku()
    other_sku = random_sku("other")
    early_batch = random_batchref("1")
    later_batch = random_batchref("2")
    other_batch = random_batchref("3")

    add_stock_with_cleanup(
        [
            (later_batch, sku, 100, "2011-01-02"),
            (early_batch, sku, 100, "2011-01-01"),
            (other_batch, other_sku, 100, None),
        ]
    )

    data = {"orderid": random_orderid(), "sku": sku, "qty": 3}
    url = config.get_api_url()

    r = requests.post(f"{url}/allocate", json=data)

    assert r.status_code == 201
    assert r.json()['batchref'] == early_batch


@pytest.mark.usefixtures("restart_api")
def test_unhappy_path_returns_400_and_error_message():
    unknown_sku, order_id = random_sku(), random_orderid()
    data = {"orderid": order_id, "sku": unknown_sku, "qty": 20}

    url = config.get_api_url()
    r = requests.post(f'{url}/allocate', json=data)
    assert r.status_code == 400
    assert r.json()["message"] == f"Invalid sku {unknown_sku}"
