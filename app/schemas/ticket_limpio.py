from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class TicketLimpioResponse(BaseModel):
    """Ticket procesado por el ETL, con datos normalizados y campos calculados."""
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