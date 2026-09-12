from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.enums import TipoDocumento
from app.schemas.pasajero import CrearPasajeroRequest, PersonaConPasajero
from app.schemas.ticket import Ticket
from app.services.pasajero_service import crear_pasajero, obtener_pasajero

router = APIRouter(prefix="/pasajeros", tags=["Pasajeros"])


@router.post("", response_model=PersonaConPasajero, status_code=201)
def crear_pasajero_endpoint(data: CrearPasajeroRequest, db: Session = Depends(get_db)):
    persona, pasajero = crear_pasajero(db, data)
    return PersonaConPasajero(
        id_persona=persona.id_persona,
        nombre=persona.nombre,
        apellido=persona.apellido,
        fecha_nacimiento=persona.fecha_nacimiento,
        tipo_documento=pasajero.tipo_documento,
        numero_documento=pasajero.numero_documento,
        id_categoria=pasajero.id_categoria,
    )


@router.get("", response_model=list[PersonaConPasajero])
def buscar_pasajeros(
    tipo_documento: TipoDocumento | None = Query(default=None),
    numero_documento: str | None = Query(default=None, max_length=15),
    db: Session = Depends(get_db),
):
    from app.models.pasajero import Pasajero
    from app.models.persona import Persona

    query = db.query(Persona, Pasajero).join(
        Pasajero, Pasajero.id_persona == Persona.id_persona
    )
    if tipo_documento:
        query = query.filter(Pasajero.tipo_documento == tipo_documento.value)
    if numero_documento:
        query = query.filter(Pasajero.numero_documento == numero_documento)

    results = []
    for persona, pasajero in query.all():
        results.append(PersonaConPasajero(
            id_persona=persona.id_persona,
            nombre=persona.nombre,
            apellido=persona.apellido,
            fecha_nacimiento=persona.fecha_nacimiento,
            tipo_documento=pasajero.tipo_documento,
            numero_documento=pasajero.numero_documento,
            id_categoria=pasajero.id_categoria,
        ))
    return results


@router.get("/{id_persona}/tickets", response_model=list[Ticket])
def tickets_de_pasajero(id_persona: int, db: Session = Depends(get_db)):
    from app.models.ticket import Ticket as TicketModel

    obtener_pasajero(db, id_persona)
    return db.query(TicketModel).filter_by(id_persona=id_persona).all()


@router.get("/{id_persona}", response_model=PersonaConPasajero)
def obtener_pasajero_endpoint(id_persona: int, db: Session = Depends(get_db)):
    persona, pasajero = obtener_pasajero(db, id_persona)
    return PersonaConPasajero(
        id_persona=persona.id_persona,
        nombre=persona.nombre,
        apellido=persona.apellido,
        fecha_nacimiento=persona.fecha_nacimiento,
        tipo_documento=pasajero.tipo_documento,
        numero_documento=pasajero.numero_documento,
        id_categoria=pasajero.id_categoria,
    )
