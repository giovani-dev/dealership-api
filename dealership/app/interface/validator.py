from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List
from pydantic import BaseModel

from dealership.app.dto.callback import Callback, Error


class Validator(ABC):
    def __init__(self, schema: Callable[[Dict[str, Any]], BaseModel]):
        self.schema = schema

    @abstractmethod
    async def validate(self, data: Dict[str, Any]) -> Callback[List[Error]] | BaseModel:
        raise NotImplementedError
