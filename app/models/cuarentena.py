from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base import Base


class Cuarentena(Base):
    """Registros que no se pudieron corregir o emparejar con seguridad."""
    __tablename__ = "cuarentena"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fuente = Column(String(20), nullable=False, index=True)
    id_registro = Column(String(50), nullable=True)
    valor_original = Column(String(100), nullable=True)
    motivo = Column(String(200), nullable=False)
    candidato = Column(String(50), nullable=True)
    fecha_registro = Column(DateTime, server_default=func.now())