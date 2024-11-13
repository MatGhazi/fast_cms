from pydantic import BaseModel
from typing import Any, Optional

class Response_Model(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    # data: Any
