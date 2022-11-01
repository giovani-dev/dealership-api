from pydantic import BaseModel, EmailStr


class LoginDto(BaseModel):
    password: str
    email: EmailStr


class CredentialsDto(BaseModel):
    token: str
    refresh_token: str


class AuthorizationDto(BaseModel):
    Authorization: str
