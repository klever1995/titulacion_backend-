from sqlalchemy import Column, Integer, String
from app.db.base import Base


class TicketSucio(Base):
    """Datos crudos de la mesa de ayuda (antes del ETL)."""
    __tablename__ = "tickets_sucios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_ticket = Column(String(50), index=True, nullable=True)
    id_cliente = Column(String(50), nullable=True)
    fecha_apertura = Column(String(50), nullable=True)
    fecha_cierre = Column(String(50), nullable=True)
    categoria = Column(String(50), nullable=True)
    canal = Column(String(50), nullable=True)
    estado = Column(String(50), nullable=True)
    agente = Column(String(100), nullable=True)
    reabierto = Column(String(10), nullable=True)
    sla_objetivo_horas = Column(String(20), nullable=True)