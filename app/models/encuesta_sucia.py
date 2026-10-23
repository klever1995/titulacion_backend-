# ==============================
# models/encuesta_sucia.py
# Datos crudos de las encuestas (antes del ETL)
# ==============================
from sqlalchemy import Column, Integer, String
from app.db.base import Base


class EncuestaSucia(Base):
    __tablename__ = "encuestas_sucias"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Puede venir nulo (5%) o repetido
    id_ticket = Column(String(50), index=True, nullable=True)
    # Puede venir con formato irregular o ser un cliente que no existe en el CRM
    id_cliente = Column(String(50), index=True, nullable=True)
    # Texto: hay valores fuera de rango (0, 6, 10, -1) y vacíos
    satisfaccion = Column(String(20), nullable=True)
    fecha_respuesta = Column(String(50), nullable=True)