from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.db.base import Base


class ReporteCalidad(Base):
    """Métricas de calidad antes y después del ETL."""
    __tablename__ = "reporte_calidad"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    fuente = Column(String(20), nullable=False, index=True)
    dimension = Column(String(20), nullable=False, index=True)
    regla = Column(String(200), nullable=False)
    etapa = Column(String(10), nullable=False, index=True)
    registros_evaluados = Column(Integer, nullable=False)
    registros_con_error = Column(Integer, nullable=False)
    puntaje = Column(Float, nullable=False)
    fecha_calculo = Column(DateTime, server_default=func.now())