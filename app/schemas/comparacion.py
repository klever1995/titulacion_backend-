# ==============================
# app/schemas/comparacion.py
# Un ticket antes (crudo) y después (limpio) del ETL
# ==============================
from typing import List, Optional

from pydantic import BaseModel

from .encuesta_sucia import EncuestaSuciaResponse
from .kpis import CuarentenaResponse
from .ticket_limpio import TicketLimpioResponse
from .ticket_sucio import TicketSucioResponse


class ComparacionResponse(BaseModel):
    sucios: List[TicketSucioResponse]          # puede haber más de uno si el ticket venía repetido
    encuestas_sucias: List[EncuestaSuciaResponse] = []   # encuesta(s) tal como llegaron
    limpio: Optional[TicketLimpioResponse] = None
    incidencias: List[CuarentenaResponse]