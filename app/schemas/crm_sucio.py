from typing import Optional

from pydantic import BaseModel


class CrmSucioResponse(BaseModel):
    """Registro crudo del CRM expuesto por la API."""
    id_cliente: Optional[str] = None
    segmento: Optional[str] = None
    ciudad: Optional[str] = None
    fecha_alta: Optional[str] = None

    class Config:
        from_attributes = True