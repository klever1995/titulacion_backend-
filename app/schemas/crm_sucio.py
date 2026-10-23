# ==============================
# app/schemas/crm_sucio.py
# ==============================
from pydantic import BaseModel
from typing import Optional


class CrmSucioResponse(BaseModel):
    id_cliente: Optional[str] = None
    segmento: Optional[str] = None
    ciudad: Optional[str] = None
    fecha_alta: Optional[str] = None

    class Config:
        from_attributes = True