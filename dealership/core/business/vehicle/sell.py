from typing import Any, List, Literal
from dealership.app.dto.callback import Callback, Error
from dealership.app.dto.filter import FilterDto, Pagination
from dealership.app.dto.vehicle import ShellVehicleDto, VehicleCallbackDto
from dealership.app.enum.callback_status import CallbackStatus
from dealership.app.enum.error import ErrorType
from dealership.app.interface.core import Core
from dealership.infra.database.connection import Database
from sqlalchemy.orm import Session

from dealership.infra.database.models.company import Company
from dealership.infra.database.models.owner import Owner
from dealership.infra.database.models.vehicle import Vehicle


class SellVehicle(Core):
    async def execute(
        self, data: ShellVehicleDto
    ) -> Callback[List[Error] | ShellVehicleDto]:
        with Session(Database.instance.engine) as session:
            owners = (
                session.query(Owner)
                .filter(Owner.client_id == data.client_id)
                .filter(Owner.company_id == None)
                .filter(Owner.vehicle_id.in_(data.vehicles))
                .all()
            )
            if len(owners) + len(data.vehicles) > 3:
                return Callback(
                    content=Error(
                        loc=["vehicles"],
                        msg="Limit of 3 vehicles has exceeded, please do buy any vehicle",
                        type=ErrorType.InvalidInput.value,
                    ),
                    status_code=CallbackStatus.BadRequest,
                )
            (
                session.query(Owner)
                .filter(Owner.client_id == None)
                .filter(Owner.company_id == data.company_id)
                .filter(Owner.vehicle_id.in_(data.vehicles))
                .update({Owner.client_id: data.client_id, Owner.company_id: None})
            )
            session.commit()
            vehicles = (
                session.query(Owner.vehicle_id)
                .filter(Owner.client_id == data.client_id)
                .filter(Owner.company_id == None)
                .filter(Owner.vehicle_id.in_(data.vehicles))
                .all()
            )
            vehicles = [vehicle.vehicle_id for vehicle in vehicles]
            company = session.query(Company).get(data.company_id)
            if not company:
                return Callback(
                    content=Error(
                        loc=["company_id"],
                        msg="Company does not exist",
                        type=ErrorType.DoesNotExist.value,
                    ),
                    status_code=CallbackStatus.BadRequest,
                )
            return Callback(
                content=ShellVehicleDto(
                    client_id=data.client_id,
                    company_id=data.company_id,
                    vehicles=vehicles,
                ),
                status_code=CallbackStatus.Ok,
            )


class ListVehicleToSell(Core):
    async def execute(
        self, data: FilterDto[Literal["color", "model"]]
    ) -> Callback[List[Error] | Pagination[VehicleCallbackDto]]:
        with Session(Database.instance.engine) as session:
            owners = (
                session.query(Owner)
                .filter(Owner.company_id == data.user.company_id)
                .filter(Owner.client_id == None)
                .offset(0 if not data.page else data.page - 1)
                .limit(data.length)
                .all()
            )
            vehicles = (
                session.query(Vehicle)
                .filter(Vehicle.id.in_([owner.vehicle_id for owner in owners]))
                .all()
            )
            return Callback(
                content=Pagination(
                    length=data.length,
                    page=data.page,
                    results=[
                        VehicleCallbackDto(
                            id=vehicle.id,
                            model=vehicle.model.value,
                            color=vehicle.color.value,
                        )
                        for vehicle in vehicles
                    ],
                ),
                status_code=CallbackStatus.Ok,
            )
