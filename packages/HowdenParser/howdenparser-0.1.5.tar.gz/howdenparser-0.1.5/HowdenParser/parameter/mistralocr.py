from typing import Literal
from pydantic import BaseModel

class Parameter(BaseModel):
    model: str = "mistralocr:"
    result_type: Literal["md"] = "md"
    mode: bool = False