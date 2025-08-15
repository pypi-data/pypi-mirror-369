from pydantic import BaseModel


class RPCOfferRequest(BaseModel):
    sdp: str
    type: str
    options: dict = {}
