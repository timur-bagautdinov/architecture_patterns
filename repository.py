import abc

import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, batch: model.Batch) -> None:
        raise NotImplementedError
    
    @abc.abstractmethod
    def get(self, reference: str) -> model.Batch:
        raise NotImplementedError
