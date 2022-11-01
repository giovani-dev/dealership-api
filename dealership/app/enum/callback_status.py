from enum import Enum


class CallbackStatus(Enum):
    Ok = 200
    Created = 201
    Accepted = 202
    NoContent = 204
    BadRequest = 400
    Unauthorized = 401
    Forbiden = 403
    NotFound = 404
    Unprocessable = 422
    InternalServerError = 500
