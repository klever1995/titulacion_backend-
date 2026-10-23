# ==============================
# app/schemas/ticket_limpio.py
# Esquema Pydantic para TicketLimpio
# ==============================
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class TicketLimpioResponse(BaseModel):
    id_ticket: str = Field(..., description="Identificador del ticket")
    id_cliente: Optional[str] = Field(None, description="ID estandarizado")
    metodo_match: Optional[str] = Field(None, description="exacto, normalizado, aproximado o sin_match")
    fecha_apertura: Optional[datetime] = None
    fecha_cierre: Optional[datetime] = None
    categoria: str = Field(..., description="Categoría corregida")
    canal: str
    estado: str
    agente: str
    reabierto: bool
    sla_objetivo_horas: Optional[float] = None
    segmento: Optional[str] = None
    satisfaccion: Optional[float] = None
    tiempo_resolucion_horas: Optional[float] = None
    incumple_sla: Optional[bool] = None

    class Config:
        from_attributes = True