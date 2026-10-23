# ==============================
# models/cuarentena.py
# Registros que no se pudieron corregir o emparejar con seguridad
# ==============================
from sqlalchemy import Column, Integer, String, DateTime, func
from app.db.base import Base


class Cuarentena(Base):
    __tablename__ = "cuarentena"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # De qué fuente viene: crm, tickets o encuestas
    fuente = Column(String(20), nullable=False, index=True)
    # Identificador del registro afectado (id_ticket, id_cliente, etc.)
    id_registro = Column(String(50), nullable=True)
    # Valor original tal como llegó
    valor_original = Column(String(100), nullable=True)
    # Por qué quedó en cuarentena (ej. "id_cliente nulo", "ambiguo por similitud")
    motivo = Column(String(200), nullable=False)
    # Mejor candidato propuesto, si hubo emparejamiento aproximado
    candidato = Column(String(50), nullable=True)

    fecha_registro = Column(DateTime, server_default=func.now())