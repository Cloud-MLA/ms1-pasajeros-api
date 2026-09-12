from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.checkin import CheckinRequest, Checkin
from app.services.checkin_service import crear_checkin

router = APIRouter(prefix="/tickets", tags=["Check-in"])


@router.post("/{id_ticket}/checkin", response_model=Checkin, status_code=201)
def crear_checkin_endpoint(
    id_ticket: int,
    data: CheckinRequest | None = None,
    db: Session = Depends(get_db),
):
    return crear_checkin(db, id_ticket, data)
