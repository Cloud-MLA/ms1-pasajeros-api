from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.persona import Persona
from app.models.pasajero import Pasajero
from app.schemas.pasajero import CrearPasajeroRequest


def obtener_pasajero(db: Session, id_persona: int) -> tuple[Persona, Pasajero]:
    persona = db.query(Persona).filter_by(id_persona=id_persona).first()
    if not persona:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NO_ENCONTRADO", "message": "Pasajero no encontrado"}
        })
    pasajero = db.query(Pasajero).filter_by(id_persona=id_persona).first()
    if not pasajero:
        raise HTTPException(status_code=404, detail={
            "error": {"code": "NO_ENCONTRADO", "message": "Pasajero no encontrado"}
        })
    return persona, pasajero


def crear_pasajero(db: Session, data: CrearPasajeroRequest) -> tuple[Persona, Pasajero]:
    from app.models.categoria_migratoria import CategoriaMigratoria

    categoria = db.query(CategoriaMigratoria).filter_by(id=data.id_categoria).first()
    if not categoria:
        raise HTTPException(status_code=422, detail={
            "error": {"code": "CATEGORIA_NO_EXISTE", "message": f"La categoria {data.id_categoria} no existe"}
        })

    existente = (
        db.query(Pasajero)
        .filter_by(tipo_documento=data.tipo_documento.value, numero_documento=data.numero_documento)
        .first()
    )
    if existente:
        raise HTTPException(status_code=409, detail={
            "error": {"code": "DUPLICADO", "message": "Ya existe un pasajero con ese tipo_documento y numero_documento"}
        })

    try:
        persona = Persona(
            nombre=data.nombre,
            apellido=data.apellido,
            fecha_nacimiento=data.fecha_nacimiento,
        )
        db.add(persona)
        db.flush()

        pasajero = Pasajero(
            id_persona=persona.id_persona,
            tipo_documento=data.tipo_documento.value,
            numero_documento=data.numero_documento,
            id_categoria=data.id_categoria,
        )
        db.add(pasajero)
        db.commit()
        db.refresh(persona)
        db.refresh(pasajero)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail={
            "error": {"code": "DUPLICADO", "message": "Ya existe un pasajero con ese tipo_documento y numero_documento"}
        })

    return persona, pasajero
