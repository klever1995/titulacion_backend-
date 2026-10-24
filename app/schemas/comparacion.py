from typing import List, Optional

from pydantic import BaseModel

from .encuesta_sucia import EncuestaSuciaResponse
from .kpis import CuarentenaResponse
from .ticket_limpio import TicketLimpioResponse
from .ticket_sucio import TicketSucioResponse


class ComparacionResponse(BaseModel):
    """Un ticket antes (crudo) y después (limpio) del ETL."""
    sucios: List[TicketSucioResponse]
    encuestas_sucias: List[EncuestaSuciaResponse] = []
    limpio: Optional[TicketLimpioResponse] = None
    incidencias: List[CuarentenaResponse]