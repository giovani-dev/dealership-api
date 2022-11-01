from typing import Any, Generic, List, Literal, TypeVar
from pydantic import BaseModel
from dealership.app.dto.user import UserDto
from dealership.app.enum import vehicle


class ShellVehicleDto(BaseModel):
    company_id: int
    client_id: int
    vehicles: List[int]


class VehicleDto(BaseModel):
    id: int
    model: vehicle.Model
    color: vehicle.Color


class BuyVehicleDto(BaseModel):
    model: Literal["Hatch", "Sedan", "Convertible"]
    color: Literal["Yelow", "Blue", "Gray"]
    client_id: int | None
    user: UserDto


class VehicleCallbackDto(BaseModel):
    id: int
    model: Literal["Hatch", "Sedan", "Convertible"]
    color: Literal["Yelow", "Blue", "Gray"]
