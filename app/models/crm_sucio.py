# ==============================
# models/crm_sucio.py
# Datos crudos del CRM (antes del ETL)
# ==============================
from sqlalchemy import Column, Integer, String
from app.db.base import Base


class CrmSucio(Base):
    __tablename__ = "crm_sucio"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    # No es único: hay clientes repetidos, algunos con segmento en conflicto
    id_cliente = Column(String(50), index=True, nullable=True)
    segmento = Column(String(50), nullable=True)
    ciudad = Column(String(50), nullable=True)
    # Texto: llega en dos formatos distintos
    fecha_alta = Column(String(50), nullable=True)