from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.equipaje import Equipaje
from app.models.persona import Persona
from app.schemas.equipaje import CrearEquipajeRequest
from app.services.ticket_service import validar_vuelo


def crear_equipaje(db: Session, data: CrearEquipajeRequest) -> Equipaje:
    persona = db.query(Persona).filter_by(id_persona=data.id_persona).first()
    if not persona:
        raise HTTPException(status_code=422, detail={
            "error": {"code": "PERSONA_NO_EXISTE", "message": f"La persona {data.id_persona} no existe"}
        })

    validar_vuelo(data.id_vuelo)

    existente = db.query(Equipaje).filter_by(id=data.id).first()
    if existente:
        raise HTTPException(status_code=409, detail={
            "error": {"code": "DUPLICADO", "message": f"Ya existe equipaje con tag ID {data.id}"}
        })

    try:
        equipaje = Equipaje(
            id=data.id,
            peso=data.peso,
            id_persona=data.id_persona,
            id_vuelo=data.id_vuelo,
        )
        db.add(equipaje)
        db.commit()
        db.refresh(equipaje)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail={
            "error": {"code": "DUPLICADO", "message": f"Ya existe equipaje con tag ID {data.id}"}
        })
    return equipaje
