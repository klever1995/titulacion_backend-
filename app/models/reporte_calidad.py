# ==============================
# models/reporte_calidad.py
# Métricas de calidad antes y después del ETL
# ==============================
from sqlalchemy import Column, Integer, String, Float, DateTime, func
from app.db.base import Base


class ReporteCalidad(Base):
    __tablename__ = "reporte_calidad"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # crm, tickets o encuestas
    fuente = Column(String(20), nullable=False, index=True)
    # completitud, unicidad, consistencia o validez
    dimension = Column(String(20), nullable=False, index=True)
    # Regla evaluada (ej. "fecha_cierre no nula en tickets cerrados")
    regla = Column(String(200), nullable=False)
    # Etapa: "antes" o "despues"
    etapa = Column(String(10), nullable=False, index=True)

    registros_evaluados = Column(Integer, nullable=False)
    registros_con_error = Column(Integer, nullable=False)
    # Porcentaje de cumplimiento de 0 a 100
    puntaje = Column(Float, nullable=False)

    fecha_calculo = Column(DateTime, server_default=func.now())