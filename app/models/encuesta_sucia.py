from sqlalchemy import Column, Integer, String
from app.db.base import Base


class EncuestaSucia(Base):
    """Datos crudos de las encuestas (antes del ETL)."""
    __tablename__ = "encuestas_sucias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_ticket = Column(String(50), index=True, nullable=True)
    id_cliente = Column(String(50), index=True, nullable=True)
    satisfaccion = Column(String(20), nullable=True)
    fecha_respuesta = Column(String(50), nullable=True)