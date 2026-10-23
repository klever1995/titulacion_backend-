# ==============================
# app/schemas/encuesta_sucia.py
# ==============================
from pydantic import BaseModel
from typing import Optional


class EncuestaSuciaResponse(BaseModel):
    id_ticket: Optional[str] = None
    id_cliente: Optional[str] = None
    satisfaccion: Optional[str] = None
    fecha_respuesta: Optional[str] = None

    class Config:
        from_attributes = True