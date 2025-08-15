from pydantic import BaseModel
from sona.core.messages import Result


class SonaResponse(BaseModel):
    code: str = "000"
    message: str = ""
    result: Result = None
