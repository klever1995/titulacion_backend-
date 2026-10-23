# ==============================
# app/schemas/kpis.py
# Esquemas Pydantic para KPIs y Calidad de Datos
# ==============================
from pydantic import BaseModel
from typing import List, Optional


class KPIsResponse(BaseModel):
    total_tickets: int
    tiempo_promedio: float
    satisfaccion_promedio: float
    reincidencia: float
    cumplimiento_sla: float
    tasa_escalamiento: Optional[float] = None
    backlog: Optional[int] = None  # tickets abiertos


class CalidadDatosResponse(BaseModel):
    # Antes del ETL
    completitud_antes: float
    unicidad_antes: float
    consistencia_antes: float
    validez_antes: float
    puntaje_total_antes: float

    # Después del ETL
    completitud_despues: float
    unicidad_despues: float
    consistencia_despues: float
    validez_despues: float
    puntaje_total_despues: float


class ReglaCalidadResponse(BaseModel):
    fuente: str
    dimension: str
    regla: str
    etapa: str
    registros_evaluados: int
    registros_con_error: int
    puntaje: float

    class Config:
        from_attributes = True


class CuarentenaResponse(BaseModel):
    fuente: str
    id_registro: Optional[str] = None
    valor_original: Optional[str] = None
    motivo: str
    candidato: Optional[str] = None

    class Config:
        from_attributes = True


class PerfiladoResponse(BaseModel):
    """Resumen de problemas encontrados en los datos crudos, por fuente."""
    fuente: str
    total_registros: int
    problemas: List[ReglaCalidadResponse]