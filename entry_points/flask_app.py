from datetime import datetime
from flask import Flask, request

from adapters import orm
from domain import model
from service_layer import services, unit_of_work


app = Flask(__name__)
orm.start_mappers()


@app.get("/")
def index() -> str:
    return "OK"


@app.route("/allocate", methods=["POST"])
def allocate_endpoint() -> tuple[dict[str, str], int]:
    try:
        batchref = services.allocate(request.json["orderid"],
                                     request.json["sku"],
                                     request.json["qty"],
                                     unit_of_work.SQLAlchemyUnitOfWork())
    except (model.OutOfStock, services.InvalidSKU) as exc:
        return {"message": str(exc)}, 400
    
    return {"batchref": batchref}, 201


@app.route("/add_batch", methods=["POST"])
def add_batch_endpoint() -> tuple[dict[str, str], int]:
    eta = request.json["eta"]
    if eta is not None:
        eta = datetime.fromisoformat(eta).date()
    
    services.add_batch(
        request.json["ref"],
        request.json["sku"],
        request.json["qty"],
        eta,
        unit_of_work.SQLAlchemyUnitOfWork(),
    )

    return {"batchref": request.json["ref"]}, 201
