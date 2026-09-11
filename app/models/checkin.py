from sqlalchemy import (
    Column,
    BigInteger,
    ForeignKey,
    TIMESTAMP,
    String,
    Boolean,
    func,
)

from app.database import Base


class Checkin(Base):
    __tablename__ = "checkin"

    id_ticket = Column(
        BigInteger,
        ForeignKey("ticket.id_ticket", ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
    )
    fecha_hora = Column(TIMESTAMP, nullable=False, server_default=func.now())
    counter = Column(String(10))
    con_equipaje = Column(Boolean, nullable=False, server_default="0")
