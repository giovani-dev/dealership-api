from datetime import datetime, timedelta
from typing import List
from uuid import uuid4

from dealership.app.dto.auth import CredentialsDto, LoginDto
from dealership.app.enum.callback_status import CallbackStatus
from dealership.app.interface.core import Core
from dealership.app.dto.callback import Callback, Error
from dealership.infra.database.connection import Database
from dealership.infra.database.models.user import User
from dealership.infra.database.models.claim import Claim
from dealership.app.enum.error import ErrorType
from dealership.app.settings import Settings
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from passlib.hash import pbkdf2_sha256
from jose import jwt
from jose.constants import ALGORITHMS


class Login(Core):
    async def execute(self, data: LoginDto) -> Callback[List[Error] | CredentialsDto]:
        invalid_user_err = Callback(
            content=Error(
                loc=[["email"], ["password"]],
                msg="Invalid user",
                type=ErrorType.InvalidInput.value,
            ),
            status_code=CallbackStatus.Unauthorized,
        )
        with Session(Database.instance.engine) as session:
            try:
                user = session.query(User).filter(User.email == data.email).one()
            except NoResultFound:
                return invalid_user_err
            if not pbkdf2_sha256.verify(data.password, user.password):
                return invalid_user_err
            try:
                claims = (
                    session.query(Claim.name).filter(Claim.user_id == user.id).all()
                )
                claims = [claim[0].name for claim in claims if claim]
                token_id = str(uuid4())
                return Callback(
                    content=CredentialsDto(
                        token=jwt.encode(
                            claims={
                                "type": "token",
                                "token_id": token_id,
                                "claims": claims,
                                "user": user.id,
                                "exp": datetime.timestamp(
                                    datetime.now()
                                    + timedelta(hours=Settings.JWT_TOKEN_TIME_TO_EXPIRE)
                                ),
                            },
                            key=Settings.JWT_SECRET_KEY,
                            algorithm=ALGORITHMS.HS512,
                        ),
                        refresh_token=jwt.encode(
                            claims={
                                "type": "refresh",
                                "token_id": token_id,
                                "user": user.id,
                                "exp": datetime.timestamp(
                                    datetime.now()
                                    + timedelta(
                                        hours=Settings.JWT_REFRESH_TOKEN_TIME_TO_EXPIRE
                                    )
                                ),
                            },
                            key=Settings.JWT_SECRET_KEY,
                            algorithm=ALGORITHMS.HS512,
                        ),
                    ),
                    status_code=CallbackStatus.Ok,
                )
            except Exception as err:
                return Callback(
                    content=Error(
                        loc=["server"],
                        msg="Internal server error",
                        type=ErrorType.InternalServerError.value,
                    ),
                    status_code=CallbackStatus.InternalServerError,
                )
