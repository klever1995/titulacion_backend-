import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# URL de conexión; en Docker apunta al servicio "db" del docker-compose
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://admin:admin123@db:5432/bi_db",
)

# Motor, fábrica de sesiones y base declarativa de SQLAlchemy
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependencia de FastAPI que entrega una sesión y la cierra al terminar."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()