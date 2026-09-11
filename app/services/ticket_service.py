import logging

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.ticket import Ticket
from app.schemas.ticket import CrearTicketRequest

logger = logging.getLogger(__name__)


def validar_vuelo(id_vuelo: int) -> dict:
    settings = get_settings()
    url = f"{settings.MS2_BASE_URL}/api/vuelos/{id_vuelo}/exists"

    last_exc = None
    for attempt in range(settings.HTTP_RETRIES):
        try:
            logger.info(
                "Saliente MS1→MS2: GET %s (intento %d/%d)",
                url, attempt + 1, settings.HTTP_RETRIES,
            )
            resp = httpx.get(url, timeout=settings.HTTP_TIMEOUT_SECONDS)
            logger.info("Saliente MS1→MS2: GET %s → %s", url, resp.status_code)
            break
        except httpx.RequestError as exc:
            last_exc = exc
            logger.warning("MS2 no disponible (intento %d/%d)", attempt + 1, settings.HTTP_RETRIES)
    else:
        raise HTTPException(status_code=502, detail={
            "error": {"code": "MS2_NO_DISPONIBLE", "message": "No se pudo conectar con MS2"}
        })

    if resp.status_code == 404:
        raise HTTPException(status_code=422, detail={
            "error": {"code": "VUELO_NO_EXISTE", "message": f"El vuelo {id_vuelo} no existe en MS2"}
        })

    data = resp.json()
    if data.get("estado") == "Cancelado":
        raise HTTPException(status_code=422, detail={
            "error": {"code": "VUELO_CANCELADO", "message": f"El vuelo {id_vuelo} esta cancelado"}
        })
    return data


def crear_ticket(db: Session, data: CrearTicketRequest) -> Ticket:
    from app.models.persona import Persona

    persona = db.query(Persona).filter_by(id_persona=data.id_persona).first()
    if not persona:
        raise HTTPException(status_code=422, detail={
            "error": {"code": "PERSONA_NO_EXISTE", "message": f"La persona {data.id_persona} no existe"}
        })

    validar_vuelo(data.id_vuelo)

    ticket = Ticket(
        precio=data.precio,
        fecha_emision=data.fecha_emision,
        id_vuelo=data.id_vuelo,
        id_persona=data.id_persona,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def obtener_ticket(db: Session, id_ticket: int) -> Ticket:
    ticket = db.query(Ticket).filter_by(id_ticket=id_ticket).first()
    if not ticket:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NO_ENCONTRADO", "message": "Ticket no encontrado"}
        })
    return ticket