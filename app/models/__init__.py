from pydantic import BaseModel
from typing import Any


class Response_Model(BaseModel):
    success: bool
    message: str
    data: Any
