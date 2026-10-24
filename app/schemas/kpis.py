from typing import List, Optional

from pydantic import BaseModel


class KPIsResponse(BaseModel):
    """Indicadores clave del servicio calculados sobre tickets limpios."""
    total_tickets: int
    tiempo_promedio: float
    satisfaccion_promedio: float
    reincidencia: float
    cumplimiento_sla: float
    tasa_escalamiento: Optional[float] = None
    backlog: Optional[int] = None


class CalidadDatosResponse(BaseModel):
    """Puntajes de calidad por dimensión, antes y después del ETL."""
    completitud_antes: float
    unicidad_antes: float
    consistencia_antes: float
    validez_antes: float
    puntaje_total_antes: float
    completitud_despues: float
    unicidad_despues: float
    consistencia_despues: float
    validez_despues: float
    puntaje_total_despues: float


class ReglaCalidadResponse(BaseModel):
    """Resultado de una regla de calidad en una etapa concreta."""
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
    """Registro que no pudo corregirse o emparejarse con seguridad."""
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