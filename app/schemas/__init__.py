from app.schemas.enums import (
    TipoDocumento,
    EstadoBoarding,
    NombreCategoriaMigratoria,
    EstadoVuelo,
)
from app.schemas.error import ErrorBody, ErrorDetail
from app.schemas.pasajero import CrearPasajeroRequest, PersonaConPasajero
from app.schemas.ticket import CrearTicketRequest, Ticket
from app.schemas.checkin import CheckinRequest, Checkin
from app.schemas.equipaje import CrearEquipajeRequest, Equipaje
from app.schemas.categoria import CategoriaMigratoria

__all__ = [
    "TipoDocumento",
    "EstadoBoarding",
    "NombreCategoriaMigratoria",
    "EstadoVuelo",
    "ErrorBody",
    "ErrorDetail",
    "CrearPasajeroRequest",
    "PersonaConPasajero",
    "CrearTicketRequest",
    "Ticket",
    "CheckinRequest",
    "Checkin",
    "CrearEquipajeRequest",
    "Equipaje",
    "CategoriaMigratoria",
]
