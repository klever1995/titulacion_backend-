# ==============================
# models/ticket_sucio.py
# Modelo para almacenar los datos crudos (Antes del ETL)
# ==============================
from sqlalchemy import Column, Integer, String, Float
from app.db.base import Base

class TicketSucio(Base):
    __tablename__ = "tickets_sucios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    
    # Usamos String(50) para definir un límite lógico a los IDs
    id_ticket = Column(String(50), nullable=False)
    id_cliente = Column(String(50), nullable=True) # Aquí se verán los nulos y los guiones
    
    # Fechas guardadas como String para evidenciar los distintos formatos que llegan
    fecha_apertura = Column(String(50), nullable=True)
    fecha_cierre = Column(String(50), nullable=True)
    
    categoria = Column(String(50), nullable=True)
    canal = Column(String(50), nullable=True)
    estado = Column(String(50), nullable=True)
    agente = Column(String(100), nullable=True)
    
    reabierto = Column(Integer, default=0)
    sla_objetivo_horas = Column(Float, nullable=True)