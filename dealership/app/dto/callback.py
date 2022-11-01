from typing import Generic, List, Tuple, TypeVar
from pydantic import BaseModel
from dealership.app.enum.callback_status import CallbackStatus
from dealership.app.enum.error import ErrorType


TContent = TypeVar("TContent")


class Callback(BaseModel, Generic[TContent]):
    status_code: CallbackStatus
    content: TContent


class Error(BaseModel):
    loc: Tuple[str] | List[str] | List[List[str]]
    msg: str
    type: str
