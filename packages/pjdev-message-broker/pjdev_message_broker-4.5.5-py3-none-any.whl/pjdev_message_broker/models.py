from typing import Generic, Optional, TypeVar

from fastapi.exceptions import HTTPException
from pydantic import BaseModel, ConfigDict, Field


class MessageBaseModel(BaseModel):
    def to_bytes(self) -> bytes:
        return bytes(self.model_dump_json(), "utf-8")

    model_config = ConfigDict(populate_by_name=True, extra="ignore")


T = TypeVar("T", bound=MessageBaseModel)
M_T = TypeVar("M_T", bound=[bool, str, int])


class Message(MessageBaseModel, Generic[M_T]):
    value: M_T

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ErrorMessage(MessageBaseModel):
    status_code: int
    message: str

    @staticmethod
    def from_exception(e: Exception) -> "ErrorMessage":
        if isinstance(e, HTTPException):
            return ErrorMessage(status_code=e.status_code, message=e.detail)

        return ErrorMessage(status_code=500, message=f"{e}")


class MessageResponse(MessageBaseModel, Generic[T]):
    body: Optional[T] = Field(default=None)
    error: Optional[ErrorMessage] = None
