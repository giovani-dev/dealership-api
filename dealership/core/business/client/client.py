from typing import List
from dealership.app.dto.callback import Callback, Error
from dealership.app.dto.client import ClientDto, CreateClientDto
from dealership.app.dto.filter import FilterDto, Pagination
from dealership.app.enum.callback_status import CallbackStatus
from dealership.app.interface.core import Core
from dealership.infra.database.connection import Database
from sqlalchemy.orm import Session

from dealership.infra.database.models.client import Client
from dealership.infra.database.models.owner import Owner


class CreateClient(Core):
    async def execute(self, data: CreateClientDto) -> Callback[List[Error] | ClientDto]:
        with Session(Database.instance.engine) as session:
            client = Client(first_name=data.name, last_name=data.last_name)
            session.add(client)
            session.commit()
            return Callback(
                content=ClientDto(
                    id=client.id, name=client.first_name, last_name=client.last_name
                ),
                status_code=CallbackStatus.Created,
            )


class GetClient(Core):
    async def execute(
        self, data: FilterDto[None]
    ) -> Callback[List[Error] | Pagination[ClientDto]]:
        with Session(Database.instance.engine) as session:
            clients = (
                session.query(Client)
                .offset(0 if not data.page else data.page - 1)
                .limit(data.length)
                .all()
            )
            clients = [
                ClientDto(
                    id=client.id, name=client.first_name, last_name=client.last_name
                )
                for client in clients
            ]
        return Callback(
            content=Pagination(
                results=clients,
                page=data.page,
                length=data.length,
            ),
            status_code=CallbackStatus.Ok,
        )
