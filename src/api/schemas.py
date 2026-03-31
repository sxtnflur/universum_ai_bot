from pydantic import BaseModel
from typing_extensions import TypeVar, Generic

T = TypeVar('T', bound=BaseModel)


class BaseFalRequest(BaseModel, Generic[T]):
    request_id: str
    status: str
    payload: T


FalRequest = BaseFalRequest[dict]
