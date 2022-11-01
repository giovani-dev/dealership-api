from typing import List
from dealership.app.dto.auth import AuthorizationDto
from dealership.app.dto.callback import Callback, Error
from dealership.app.dto.user import UserDto
from dealership.app.enum.callback_status import CallbackStatus
from dealership.app.enum.error import ErrorType
from dealership.app.interface.core import Core
from dealership.app.settings import Settings
from jose import jwt
from jose.constants import ALGORITHMS
from sqlalchemy.orm import Session

from dealership.infra.database.connection import Database
from dealership.infra.database.models.user import User


class VerifyAuth(Core):
    def __init__(self, claims: List[str]) -> None:
        self.claims = claims

    async def execute(self, data: AuthorizationDto) -> Callback[List[Error] | UserDto]:
        token = data.Authorization.split(" ")
        if not token[0] == "Bearer":
            return Callback(
                content=Error(
                    loc=["header", "Authorization"],
                    msg="This is not a Bearer token",
                    type=ErrorType.InvalidInput.value,
                ),
                status_code=CallbackStatus.Unprocessable,
            )
        try:
            token = jwt.decode(
                token=token[1], key=Settings.JWT_SECRET_KEY, algorithms=ALGORITHMS.HS512
            )
        except Exception:
            return Callback(
                content=Error(
                    loc=["header", "Authorization"],
                    msg="Invalid token",
                    type=CallbackStatus.Unauthorized.value,
                ),
                status_code=CallbackStatus.Unauthorized,
            )
        for claim in self.claims:
            if not claim in token["claims"]:
                return Callback(
                    content=Error(
                        loc=["header", "Authorization"],
                        msg="Invalid token",
                        type=CallbackStatus.Unauthorized.value,
                    ),
                    status_code=CallbackStatus.Unauthorized,
                )
        with Session(Database.instance.engine) as session:
            user = session.query(User).get(token["user"])
            return Callback(
                content=UserDto(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    company_id=user.company_id,
                ),
                status_code=CallbackStatus.Ok,
            )
