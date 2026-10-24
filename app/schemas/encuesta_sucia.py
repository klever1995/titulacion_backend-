from typing import Optional

from pydantic import BaseModel


class EncuestaSuciaResponse(BaseModel):
    """Registro crudo de una encuesta expuesto por la API."""
    id_ticket: Optional[str] = None
    id_cliente: Optional[str] = None
    satisfaccion: Optional[str] = None
    fecha_respuesta: Optional[str] = None

    class Config:
        from_attributes = True