from pydantic import BaseModel


class CreateClientDto(BaseModel):
    name: str
    last_name: str


class ClientDto(BaseModel):
    id: int
    name: str
    last_name: str