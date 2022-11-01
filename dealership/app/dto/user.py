from pydantic import BaseModel, EmailStr

from dealership.app.dto.company import CompanyDto, CreateCompanyDto


class UserDto(BaseModel):
    id: int
    name: str
    email: EmailStr
    company_id: int | None


class CreateUserDto(BaseModel):
    company_id: int | None
    password: str
    name: str
    email: EmailStr


class CreateCompanyUserDto(BaseModel):
    company: CreateCompanyDto
    user: CreateUserDto


class CompanyUserDto(BaseModel):
    company: CompanyDto
    user: UserDto
