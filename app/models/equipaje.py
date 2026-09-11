from sqlalchemy import (
    Column,
    String,
    Numeric,
    Integer,
    BigInteger,
    ForeignKey,
    CheckConstraint,
)

from app.database import Base


class Equipaje(Base):
    __tablename__ = "equipaje"
    __table_args__ = (CheckConstraint("peso > 0", name="chk_equipaje_peso"),)

    id = Column(String(20), primary_key=True)
    peso = Column(Numeric(6, 2), nullable=False)
    id_persona = Column(
        Integer, ForeignKey("persona.id_persona", ondelete="RESTRICT"), nullable=False
    )
    id_vuelo = Column(BigInteger, nullable=False)
