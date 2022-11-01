from typing import List

from sqlalchemy import select
from dealership.app.dto.company import CompanyDto
from dealership.app.dto.user import (
    CompanyUserDto,
    CreateCompanyUserDto,
    CreateUserDto,
    UserDto,
)
from dealership.app.enum.callback_status import CallbackStatus
from dealership.app.enum.claims import DefaultClaims
from dealership.app.enum.error import ErrorType
from dealership.app.interface.core import Core
from dealership.app.dto.callback import Callback, Error
from dealership.infra.database.connection import Database
from dealership.infra.database.models.company import Company
from dealership.infra.database.models.user import User
from dealership.infra.database.models.claim import Claim
from sqlalchemy.orm import Session
from passlib.hash import pbkdf2_sha256


class CreateUserCore(Core):
    def __init__(self, claims: List[DefaultClaims]) -> None:
        self.claims = claims

    async def execute(self, data: CreateUserDto) -> Callback[List[Error] | UserDto]:
        with Session(Database.instance.engine) as session:
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
            user = session.query(User).filter(User.email == data.email)
            if session.query(user.exists()).scalar() >= 1:
                return Callback(
                    content=Error(
                        loc=["email"],
                        msg="Email already exist",
                        type=ErrorType.AlreadyExist.value,
                    ),
                    status_code=CallbackStatus.BadRequest,
                )
            user = User(
                name=data.name,
                email=data.email,
                password=pbkdf2_sha256.hash(data.password),
                company_id=data.company_id,
            )
            session.add(user)
            session.commit()
            claims = [Claim(name=claim, user_id=user.id) for claim in self.claims]
            session.add_all(claims)
            session.commit()
            return Callback(
                content=UserDto(
                    id=user.id,
                    name=data.name,
                    email=data.email,
                    company_id=data.company_id,
                ),
                status_code=CallbackStatus.Created,
            )


class CreateCompanyUser(Core):
    def __init__(self, user: Core) -> None:
        self.user = user

    async def execute(
        self, data: CreateCompanyUserDto
    ) -> Callback[List[Error] | CompanyUserDto]:
        with Session(Database.instance.engine) as session:
            company = session.query(Company).filter(Company.cnpj == data.company.cnpj)
            if session.query(company.exists()).scalar():
                return Callback(
                    content=Error(
                        loc=["company", "cnpj"],
                        msg="This company already exist",
                        type=ErrorType.AlreadyExist.value,
                    ),
                    status_code=CallbackStatus.BadRequest,
                )
            company = Company(
                company_name=data.company.name,
                owner_name=data.company.owner_name,
                cnpj=data.company.cnpj,
            )
            session.add(company)
            session.commit()
            user = data.user.dict()
            user.update({"company_id": company.id})
            user = await self.user.execute(data=CreateUserDto(**user))
            if user.status_code.value >= 400:
                session.query(Company).filter(Company.id == company.id).delete(
                    synchronize_session=False
                )
                session.commit()
                return user
            return Callback(
                content=CompanyUserDto(
                    company=CompanyDto(
                        id=company.id,
                        name=data.company.name,
                        cnpj=data.company.cnpj,
                        owner_name=data.company.owner_name,
                    ),
                    user=user.content,
                ),
                status_code=CallbackStatus.Created,
            )
