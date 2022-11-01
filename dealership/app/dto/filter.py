from typing import Generic, List, TypeVar
from pydantic import BaseModel

from dealership.app.dto.user import UserDto


T = TypeVar("T")


class FilterDto(Generic[T], BaseModel):
    page: int = 0
    length: int = 5
    user: UserDto | None
    order_by: T | None


class Pagination(Generic[T], BaseModel):
    results: List[T]
    page: int
    length: int
