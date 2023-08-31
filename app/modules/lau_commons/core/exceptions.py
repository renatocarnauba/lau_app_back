from typing import Type

from fastapi import HTTPException


class UserNotFound(HTTPException):
    def __init__(self) -> None:
        status_code = 404
        detail = "User not found"
        super().__init__(status_code=status_code, detail=detail)


class UserWithoutPrivileges(HTTPException):
    def __init__(self) -> None:
        status_code = 400
        detail = "The user doesn't have enough privileges"
        super().__init__(status_code=status_code, detail=detail)


class UserAlreadyExists(HTTPException):
    def __init__(self) -> None:
        status_code = 400
        detail = "The user with this username already exists in the system"
        super().__init__(status_code=status_code, detail=detail)


class UserInactive(HTTPException):
    def __init__(self) -> None:
        status_code = 400
        detail = "Inactive user"
        super().__init__(status_code=status_code, detail=detail)


class LoginFail(HTTPException):
    def __init__(self) -> None:
        status_code = 400
        detail = "Incorrect email or password"
        super().__init__(status_code=status_code, detail=detail)


class InvalidCredential(HTTPException):
    def __init__(self) -> None:
        status_code = 403
        detail = "Could not validate credentials"
        super().__init__(status_code=status_code, detail=detail)


class AccountNotFound(HTTPException):
    def __init__(self) -> None:
        status_code = 404
        detail = "Account not found"
        super().__init__(status_code=status_code, detail=detail)


class CategoryNotFound(HTTPException):
    def __init__(self) -> None:
        status_code = 404
        detail = "Category not found"
        super().__init__(status_code=status_code, detail=detail)


class InstitutionNotFound(HTTPException):
    def __init__(self) -> None:
        status_code = 404
        detail = "Institution not found"
        super().__init__(status_code=status_code, detail=detail)


class TransactionNotFound(HTTPException):
    def __init__(self) -> None:
        status_code = 404
        detail = "Transaction not found"
        super().__init__(status_code=status_code, detail=detail)


ErrorBase = (
    Type[UserNotFound]
    | Type[UserWithoutPrivileges]
    | Type[UserAlreadyExists]
    | Type[UserInactive]
    | Type[LoginFail]
    | Type[InvalidCredential]
    | Type[AccountNotFound]
    | Type[CategoryNotFound]
    | Type[InstitutionNotFound]
    | Type[TransactionNotFound]
)
