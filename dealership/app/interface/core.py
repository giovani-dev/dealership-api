from abc import ABC, abstractmethod
from typing import List

from pydantic import BaseModel

from dealership.app.dto.callback import Callback, Error


class Core(ABC):
    @abstractmethod
    async def execute(self, data: BaseModel) -> Callback[List[Error] | BaseModel]:
        raise NotImplementedError
