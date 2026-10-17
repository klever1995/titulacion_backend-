# ==============================
# app/schemas/kpis.py
# Esquema Pydantic para los KPIs
# ==============================
from pydantic import BaseModel

class KPIsResponse(BaseModel):
    total_tickets: int
    tiempo_promedio: float
    satisfaccion_promedio: float
    reincidencia: float