# ==============================
# models/ticket_sucio.py
# Datos crudos de la mesa de ayuda (antes del ETL)
# ==============================
from sqlalchemy import Column, Integer, String
from app.db.base import Base


class TicketSucio(Base):
    __tablename__ = "tickets_sucios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Todo se guarda como texto para conservar los errores tal como llegan
    # (duplicados, formatos distintos, valores raros). No es único a propósito.
    id_ticket = Column(String(50), index=True, nullable=True)
    id_cliente = Column(String(50), nullable=True)

    fecha_apertura = Column(String(50), nullable=True)
    fecha_cierre = Column(String(50), nullable=True)

    categoria = Column(String(50), nullable=True)
    canal = Column(String(50), nullable=True)
    estado = Column(String(50), nullable=True)
    agente = Column(String(100), nullable=True)

    # Llega como 0/1 pero a veces como "Sí"/"No"
    reabierto = Column(String(10), nullable=True)
    # Llega como número, vacío o negativo
    sla_objetivo_horas = Column(String(20), nullable=True)