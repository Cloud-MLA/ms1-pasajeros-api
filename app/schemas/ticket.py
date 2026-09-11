from datetime import date

from pydantic import BaseModel

from app.schemas.enums import EstadoBoarding


class CrearTicketRequest(BaseModel):
    precio: float
    fecha_emision: date
    id_vuelo: int
    id_persona: int


class Ticket(BaseModel):
    id_ticket: int
    precio: float
    fecha_emision: date
    estado_boarding: EstadoBoarding
    id_vuelo: int
    id_persona: int

    class Config:
        from_attributes = True
