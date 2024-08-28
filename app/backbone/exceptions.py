from typing import Any
from fastapi import HTTPException, status


class ValidationException(HTTPException):
    def __init__(
        self,
        detail: Any,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            status.HTTP_400_BAD_REQUEST,
            detail,
            headers,
        )


class ItemNotFoundException(HTTPException):
    def __init__(
        self,
        item_type: str,
        id: int,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f"{item_type} with id {id} was not found",
            headers,
        )


class NameNotFoundException(HTTPException):
    def __init__(
        self,
        item_type: str,
        name: str,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            status.HTTP_404_NOT_FOUND,
            f"{item_type} '{name}' was not found",
            headers,
        )
