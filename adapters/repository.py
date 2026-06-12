import abc

from domain import model
from sqlalchemy.orm import Session


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, product: model.Product) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def get(self, reference: str) -> model.Product | None:
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository):
    def __init__(self, session: Session) -> None:
        self.session = session
    
    def add(self, product: model.Product) -> None:
        self.session.add(product)
    
    def get(self, sku: str) -> model.Product | None:
        return self.session.query(model.Product).filter_by(sku=sku).first()
