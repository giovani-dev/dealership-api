from pydantic import BaseModel


class CreateCompanyDto(BaseModel):
    name: str
    cnpj: str
    owner_name: str


class CompanyDto(BaseModel):
    id: int
    name: str
    cnpj: str
    owner_name: str
