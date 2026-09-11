from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.ticket import CrearTicketRequest, Ticket
from app.services.ticket_service import crear_ticket, obtener_ticket

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.post("", response_model=Ticket, status_code=201)
def crear_ticket_endpoint(data: CrearTicketRequest, db: Session = Depends(get_db)):
    return crear_ticket(db, data)


@router.get("", response_model=list[Ticket])
def buscar_tickets(
    vuelo_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    from app.models.ticket import Ticket as TicketModel

    query = db.query(TicketModel)
    if vuelo_id is not None:
        query = query.filter(TicketModel.id_vuelo == vuelo_id)
    return query.all()


@router.get("/{id_ticket}", response_model=Ticket)
def obtener_ticket_endpoint(id_ticket: int, db: Session = Depends(get_db)):
    return obtener_ticket(db, id_ticket)
