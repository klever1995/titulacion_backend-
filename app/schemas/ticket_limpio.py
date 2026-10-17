# ==============================
# app/schemas/ticket_limpio.py
# Esquema Pydantic para TicketLimpio
# ==============================
from pydantic import BaseModel, Field
from typing import Optional

class TicketLimpioResponse(BaseModel):
    id_ticket: str = Field(..., description="Identificador del ticket")
    id_cliente: Optional[str] = Field(None, description="ID estandarizado")
    fecha_apertura: Optional[str]
    fecha_cierre: Optional[str]
    categoria: str = Field(..., description="Categoría corregida (ej. Soporte)")
    canal: str
    estado: str
    agente: str
    reabierto: int
    sla_objetivo_horas: float
    segmento: Optional[str] = None
    satisfaccion: Optional[float] = None
    tiempo_resolucion_horas: float

    class Config:
        from_attributes = True