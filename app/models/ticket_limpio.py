# ==============================
# models/ticket_limpio.py
# Modelo para almacenar los datos procesados (Después del ETL)
# ==============================
from sqlalchemy import Column, Integer, String, Float
from app.db.base import Base

class TicketLimpio(Base):
    __tablename__ = "tickets_limpios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # En la tabla limpia, el id_ticket es único y el id_cliente ya está estandarizado
    id_ticket = Column(String(50), unique=True, index=True, nullable=False)
    id_cliente = Column(String(50), index=True, nullable=True)
    
    # Las fechas ya están estandarizadas al formato YYYY-MM-DD HH:MM:SS
    fecha_apertura = Column(String(50), nullable=True)
    fecha_cierre = Column(String(50), nullable=True)
    
    # Categorías ya corregidas (ej. "Soporte" en lugar de "SOPORTE")
    categoria = Column(String(50), nullable=False)
    canal = Column(String(50), nullable=False)
    estado = Column(String(50), nullable=False)
    agente = Column(String(100), nullable=False)
    
    reabierto = Column(Integer, default=0)
    sla_objetivo_horas = Column(Float, nullable=False)
    
    # Nuevos campos que se agregan al hacer el JOIN con el CRM y Encuestas
    segmento = Column(String(50), nullable=True)
    satisfaccion = Column(Float, nullable=True)
    
    # Campo calculado durante el ETL
    tiempo_resolucion_horas = Column(Float, nullable=False, default=0.0)