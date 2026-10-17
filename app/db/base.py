# ==============================
# app/db/base.py
# Configuración de base de datos PostgreSQL
# ==============================
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Apunta al servicio "db" que definiremos en el docker-compose
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://admin:admin123@db:5432/bi_db")

engine = create_engine(DATABASE_URL)

# Crear la fábrica de sesiones
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para los modelos
Base = declarative_base()

# Dependencia para obtener sesión de BD en FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()