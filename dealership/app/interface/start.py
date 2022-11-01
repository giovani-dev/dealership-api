from abc import ABC, abstractmethod
from typing import Generic, TypeVar


class Starter(ABC):
    @abstractmethod
    def start(self):
        raise NotImplementedError
