from datetime import datetime

from pydantic import BaseModel


class CheckinRequest(BaseModel):
    counter: str | None = None
    con_equipaje: bool = False


class Checkin(BaseModel):
    id_ticket: int
    fecha_hora: datetime
    counter: str | None = None
    con_equipaje: bool

    class Config:
        from_attributes = True
