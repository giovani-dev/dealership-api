from typing import Any, Dict, List

from pydantic import BaseModel

from dealership.app.dto.callback import Callback, Error
from dealership.app.interface.core import Core
from dealership.app.interface.validator import Validator


class Mediator:
    def __init__(self, validator: Validator, core: Core):
        self.validator = validator
        self.core = core

    async def mediate(self, data: Dict[str, Any]) -> Callback[List[Error] | BaseModel]:
        data = await self.validator.validate(data)
        if isinstance(data, Callback):
            return data
        return await self.core.execute(data)
