from sqlalchemy import (
    Column,
    BigInteger,
    Integer,
    Date,
    Numeric,
    String,
    Enum,
    ForeignKey,
    CheckConstraint,
)

from app.database import Base


class Ticket(Base):
    __tablename__ = "ticket"
    __table_args__ = (CheckConstraint("estado_boarding <> ''", name="chk_ticket_estado"),)

    id_ticket = Column(BigInteger, primary_key=True, autoincrement=True)
    precio = Column(Numeric(10, 2), nullable=False)
    fecha_emision = Column(Date, nullable=False)
    estado_boarding = Column(
        Enum(
            "Emitido",
            "Check-in",
            "Embarcado",
            "No-show",
            "Cancelado",
            name="estado_boarding",
        ),
        nullable=False,
        server_default="Emitido",
    )
    id_vuelo = Column(BigInteger, nullable=False)
    id_persona = Column(
        Integer, ForeignKey("persona.id_persona"), nullable=False
    )
