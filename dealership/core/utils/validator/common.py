from pydantic import BaseModel, ValidationError
from typing import Dict, Any, List

from dealership.app.dto.callback import Callback, Error
from dealership.app.enum.callback_status import CallbackStatus
from dealership.app.enum.error import ErrorType
from dealership.app.interface.validator import Validator as ABCValidator


class Validator(ABCValidator):
    async def validate(self, data: Dict[str, Any]) -> Callback[List[Error]] | BaseModel:
        try:
            return self.schema(**data)
        except ValidationError as err:
            return Callback(
                status_code=CallbackStatus.Unprocessable,
                content=err.errors(),
            )
        except Exception as err:
            return Callback(
                content=Error(
                    loc=["server"],
                    msg="Internal server error",
                    type=ErrorType.InternalServerError.value,
                )
            )
