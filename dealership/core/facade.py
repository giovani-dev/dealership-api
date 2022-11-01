import re
from typing import Any, Dict, List, Literal

from pydantic import BaseModel
from dealership.app.dto.auth import AuthorizationDto, CredentialsDto, LoginDto

from dealership.app.dto.callback import Callback, Error
from dealership.app.dto.client import ClientDto, CreateClientDto
from dealership.app.dto.filter import FilterDto, Pagination
from dealership.app.dto.user import (
    CreateCompanyUserDto,
    CreateUserDto,
    UserDto,
)
from dealership.app.dto.vehicle import BuyVehicleDto, ShellVehicleDto
from dealership.app.enum.claims import DefaultClaims
from dealership.core.business.auth.verify import VerifyAuth
from dealership.core.business.client.client import CreateClient, GetClient
from dealership.core.business.vehicle.buy import BuyVehicle
from dealership.core.business.vehicle.sell import ListVehicleToSell, SellVehicle
from dealership.core.utils.mediator.common import Mediator
from dealership.core.utils.validator.common import Validator
from dealership.core.business.user.create import (
    CreateCompanyUser,
    CreateUserCore,
)
from dealership.core.business.auth.login import Login
from dealership.core.business.auth.refresh import Refresh


class UserFace:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    async def create_company(self) -> Callback[List[Error] | BaseModel]:
        mediator = Mediator(
            validator=Validator(schema=CreateCompanyUserDto),
            core=CreateCompanyUser(user=CreateUserCore(claims=[DefaultClaims.Company])),
        )
        return await mediator.mediate(self.data)

    async def create_seller(self) -> Callback[List[Error] | BaseModel]:
        mediator = Mediator(
            validator=Validator(schema=CreateUserDto),
            core=CreateUserCore(claims=[DefaultClaims.Seller]),
        )
        return await mediator.mediate(self.data)


class AuthFacade:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    async def login(self) -> Callback[List[Error] | BaseModel]:
        mediator = Mediator(
            validator=Validator(schema=LoginDto),
            core=Login(),
        )
        return await mediator.mediate(self.data)

    async def refresh(self) -> Callback[List[Error] | BaseModel]:
        mediator = Mediator(
            validator=Validator(schema=CredentialsDto),
            core=Refresh(),
        )
        return await mediator.mediate(self.data)

    async def verify(self, _claims: List[str]) -> Callback[List[Error] | BaseModel]:
        mediator = Mediator(
            validator=Validator(schema=AuthorizationDto),
            core=VerifyAuth(claims=_claims),
        )
        return await mediator.mediate(self.data)


class VehicleFacade:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    async def buy(self) -> Callback[List[Error] | BaseModel]:
        mediator = Mediator(
            validator=Validator(schema=BuyVehicleDto), core=BuyVehicle()
        )
        return await mediator.mediate(self.data)

    async def get_to_sell(self):
        mediator = Mediator(
            validator=Validator(schema=FilterDto[Literal["color", "model"]]),
            core=ListVehicleToSell(),
        )
        return await mediator.mediate(self.data)

    async def sell_vehicle(self):
        mediator = Mediator(
            validator=Validator(schema=ShellVehicleDto), core=SellVehicle()
        )
        return await mediator.mediate(self.data)


class ClientFacade:
    def __init__(self, data: Dict[str, Any]) -> None:
        self.data = data

    async def create(self):
        mediator = Mediator(
            validator=Validator(schema=CreateClientDto), core=CreateClient()
        )
        return await mediator.mediate(self.data)

    async def get_clients(self):
        mediator = Mediator(
            validator=Validator(schema=FilterDto[None]), core=GetClient()
        )
        return await mediator.mediate(self.data)
