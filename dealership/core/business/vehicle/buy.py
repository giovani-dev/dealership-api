from typing import Any, List
from dealership.app.dto.callback import Callback, Error
from dealership.app.dto.company import CompanyDto
from dealership.app.dto.user import UserDto
from dealership.app.dto.vehicle import (
    VehicleCallbackDto,
    BuyVehicleDto,
)
from dealership.app.enum.callback_status import CallbackStatus
from dealership.app.enum.error import ErrorType
from dealership.app.interface.core import Core
from dealership.infra.database.connection import Database
from dealership.infra.database.models.owner import Owner, OwnerHistory
from dealership.infra.database.models.vehicle import Vehicle
from sqlalchemy.orm import Session


class BuyVehicle(Core):
    async def execute(
        self, data: BuyVehicleDto
    ) -> Callback[List[Error] | VehicleCallbackDto]:
        with Session(Database.instance.engine) as session:
            vehicle = Vehicle(
                model=data.model,
                color=data.color,
            )
            session.add(vehicle)
            session.commit()
            if not data.client_id:
                owner = Owner(
                    company_id=data.user.company_id,
                    client_id=None,
                    vehicle_id=vehicle.id,
                )
            else:
                owner = Owner(
                    company_id=None,
                    client_id=data.client_id,
                    vehicle_id=vehicle.id,
                )
            session.add(owner)
            session.commit()
            owner_history = OwnerHistory(
                owner_id=owner.id,
                owner_client_id=owner.client_id,
                owner_company_id=owner.company_id,
            )
            session.add(owner_history)
            session.commit()
            return Callback(
                content=VehicleCallbackDto(
                    id=vehicle.id, model=data.model, color=data.color
                ),
                status_code=CallbackStatus.Created,
            )
