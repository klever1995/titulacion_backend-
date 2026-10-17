# ==============================
# app/schemas/ticket_sucio.py
# Esquema Pydantic para TicketSucio
# ==============================
from pydantic import BaseModel, Field
from typing import Optional

class TicketSucioResponse(BaseModel):
    id_ticket: str = Field(..., description="Identificador del ticket original")
    id_cliente: Optional[str] = Field(None, description="ID del cliente tal como llegó (con guiones o nulo)")
    fecha_apertura: Optional[str] = Field(None, description="Fecha en formato original")
    fecha_cierre: Optional[str] = Field(None, description="Fecha en formato original")
    categoria: str = Field(..., description="Categoría sin estandarizar")
    canal: str
    estado: str
    agente: str
    reabierto: int
    sla_objetivo_horas: float

    class Config:
        from_attributes = True