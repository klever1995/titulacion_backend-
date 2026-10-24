from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from app.db.base import Base


class TicketLimpio(Base):
    """Tickets procesados (después del ETL)."""
    __tablename__ = "tickets_limpios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_ticket = Column(String(50), unique=True, index=True, nullable=False)
    id_cliente = Column(String(50), index=True, nullable=True)
    metodo_match = Column(String(20), nullable=True)
    fecha_apertura = Column(DateTime, nullable=True)
    fecha_cierre = Column(DateTime, nullable=True)
    categoria = Column(String(50), nullable=False)
    canal = Column(String(50), nullable=False)
    estado = Column(String(50), nullable=False)
    agente = Column(String(100), nullable=False, default="Sin asignar")
    reabierto = Column(Boolean, nullable=False, default=False)
    sla_objetivo_horas = Column(Float, nullable=True)
    segmento = Column(String(50), nullable=True)
    satisfaccion = Column(Float, nullable=True)
    tiempo_resolucion_horas = Column(Float, nullable=True)
    incumple_sla = Column(Boolean, nullable=True)