# ==============================
# models/ticket_limpio.py
# Tickets procesados (después del ETL)
# ==============================
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from app.db.base import Base


class TicketLimpio(Base):
    __tablename__ = "tickets_limpios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # Aquí sí es único: los duplicados ya se eliminaron
    id_ticket = Column(String(50), unique=True, index=True, nullable=False)
    # Puede ser nulo si el cliente quedó en cuarentena
    id_cliente = Column(String(50), index=True, nullable=True)
    # Cómo se emparejó el cliente: exacto, normalizado, aproximado o sin_match
    metodo_match = Column(String(20), nullable=True)

    # Fechas reales para poder calcular horas y filtrar por período
    fecha_apertura = Column(DateTime, nullable=True)
    fecha_cierre = Column(DateTime, nullable=True)

    categoria = Column(String(50), nullable=False)
    canal = Column(String(50), nullable=False)
    estado = Column(String(50), nullable=False)
    # Hay tickets sin agente: se guarda como "Sin asignar"
    agente = Column(String(100), nullable=False, default="Sin asignar")

    reabierto = Column(Boolean, nullable=False, default=False)
    sla_objetivo_horas = Column(Float, nullable=True)

    # Datos que vienen del CRM y de las encuestas
    segmento = Column(String(50), nullable=True)
    satisfaccion = Column(Float, nullable=True)

    # Calculados en el ETL. Nulos si el ticket sigue abierto o tiene datos inválidos
    tiempo_resolucion_horas = Column(Float, nullable=True)
    incumple_sla = Column(Boolean, nullable=True)