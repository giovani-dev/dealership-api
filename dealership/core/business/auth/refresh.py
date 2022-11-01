from datetime import datetime, timedelta
from re import L
from typing import List
from uuid import uuid4
from dealership.app.dto.auth import CredentialsDto, LoginDto
from dealership.app.enum.callback_status import CallbackStatus
from dealership.app.enum.error import ErrorType
from dealership.app.interface.core import Core
from dealership.app.dto.callback import Callback, Error
from dealership.app.settings import Settings
from jose import jwt
from jose.constants import ALGORITHMS
from jose.exceptions import ExpiredSignatureError


class Refresh(Core):
    async def execute(
        self, data: CredentialsDto
    ) -> Callback[List[Error] | CredentialsDto]:
        token = jwt.decode(
            token=data.token,
            options={"verify_signature": False, 'verify_exp': False},
            key=Settings.JWT_SECRET_KEY,
        )
        try:
            refresh_token = jwt.decode(
                token=data.refresh_token,
                key=Settings.JWT_SECRET_KEY,
                algorithms=ALGORITHMS.HS512,
            )
        except ExpiredSignatureError:
            return Callback(
                content=Error(
                    loc=["refresh_token"],
                    msg="Refresh token expired",
                    type=ErrorType.InvalidInput.value,
                ),
                status_code=CallbackStatus.Forbiden,
            )
        if (
            refresh_token["type"] != "refresh"
            or token["type"] != "token"
            or token["token_id"] != refresh_token["token_id"]
        ):
            return Callback(
                content=Error(
                    loc=[["token"], ["refresh_token"]],
                    msg="Invalid credentials",
                    type=ErrorType.InvalidInput.value,
                ),
                status_code=CallbackStatus.Forbiden,
            )
        token_id = str(uuid4())
        return Callback(
            content=CredentialsDto(
                token=jwt.encode(
                    claims={
                        "type": token["type"],
                        "token_id": token_id,
                        "claims": token["claims"],
                        "user": token["user"],
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
                        "type": refresh_token["type"],
                        "token_id": token_id,
                        "user": refresh_token["user"],
                        "exp": datetime.timestamp(
                            datetime.now()
                            + timedelta(hours=Settings.JWT_REFRESH_TOKEN_TIME_TO_EXPIRE)
                        ),
                    },
                    key=Settings.JWT_SECRET_KEY,
                    algorithm=ALGORITHMS.HS512,
                ),
            ),
            status_code=CallbackStatus.Ok,
        )
