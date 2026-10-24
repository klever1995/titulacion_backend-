from sqlalchemy import Column, Integer, String
from app.db.base import Base


class CrmSucio(Base):
    """Datos crudos del CRM (antes del ETL)."""
    __tablename__ = "crm_sucio"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    id_cliente = Column(String(50), index=True, nullable=True)
    segmento = Column(String(50), nullable=True)
    ciudad = Column(String(50), nullable=True)
    fecha_alta = Column(String(50), nullable=True)