from typing import Optional

from pydantic import BaseModel, Field

class TicketSucioResponse(BaseModel):
    """Ticket crudo tal como llegó, sin normalizar."""
    id_ticket: Optional[str] = Field(None, description="Identificador del ticket original")
    id_cliente: Optional[str] = Field(None, description="ID del cliente tal como llegó (con guiones, espacios o nulo)")
    fecha_apertura: Optional[str] = Field(None, description="Fecha en formato original")
    fecha_cierre: Optional[str] = Field(None, description="Fecha en formato original")
    categoria: Optional[str] = Field(None, description="Categoría sin estandarizar")
    canal: Optional[str] = None
    estado: Optional[str] = None
    agente: Optional[str] = None
    reabierto: Optional[str] = Field(None, description="0/1 o Sí/No según llegó")
    sla_objetivo_horas: Optional[str] = Field(None, description="Valor original, puede ser vacío o negativo")

    class Config:
        from_attributes = True