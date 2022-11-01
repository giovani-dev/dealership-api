from enum import Enum


class ErrorType(Enum):
    AlreadyExist = "validation.already_exist"
    DoesNotExist = "validation.does_not_exist"
    InvalidInput = "validation.invalid_input"
    InternalServerError = "server.internal_server_error"
