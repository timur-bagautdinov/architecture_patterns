import config
from adapters import orm, repository
from domain import model
from service_layer import services


from flask import Flask, request
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


app = Flask(__name__)
orm.start_mappers()
get_session = sessionmaker(bind=create_engine(config.get_postgres_url()))


@app.get("/")
def index() -> str:
    return "OK"


@app.route("/allocate", methods=["POST"])
def allocate_endpoint() -> tuple[dict[str, str], int]:
    session = get_session()
    repo = repository.SQLAlchemyRepository(session)

    try:
        batchref = services.allocate(request.json["orderid"],
                                     request.json["sku"],
                                     request.json["qty"],  repo, session)
    except (model.OutOfStock, services.InvalidSKU) as exc:
        return {"message": str(exc)}, 400
    
    return {"batchref": batchref}, 201
