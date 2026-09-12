from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.checkin import Checkin
from app.models.ticket import Ticket
from app.schemas.checkin import CheckinRequest


def crear_checkin(db: Session, id_ticket: int, data: CheckinRequest | None = None) -> Checkin:
    ticket = db.query(Ticket).filter_by(id_ticket=id_ticket).first()
    if not ticket:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NO_ENCONTRADO", "message": "Ticket no encontrado"}
        })

    existente = db.query(Checkin).filter_by(id_ticket=id_ticket).first()
    if existente:
        raise HTTPException(status_code=409, detail={
            "error": {"code": "DUPLICADO", "message": "El ticket ya tiene check-in registrado"}
        })

    checkin = Checkin(
        id_ticket=id_ticket,
        counter=data.counter if data else None,
        con_equipaje=data.con_equipaje if data else False,
    )
    db.add(checkin)
    db.commit()
    db.refresh(checkin)
    return checkin
