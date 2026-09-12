from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.equipaje import CrearEquipajeRequest, Equipaje
from app.services.equipaje_service import crear_equipaje

router = APIRouter(prefix="/equipajes", tags=["Equipajes"])


@router.post("", response_model=Equipaje, status_code=201)
def crear_equipaje_endpoint(data: CrearEquipajeRequest, db: Session = Depends(get_db)):
    return crear_equipaje(db, data)


@router.get("", response_model=list[Equipaje])
def buscar_equipajes(
    pasajero_id: int | None = Query(default=None),
    vuelo_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    from app.models.equipaje import Equipaje as EquipajeModel

    query = db.query(EquipajeModel)
    if pasajero_id is not None:
        query = query.filter(EquipajeModel.id_persona == pasajero_id)
    if vuelo_id is not None:
        query = query.filter(EquipajeModel.id_vuelo == vuelo_id)
    return query.all()
