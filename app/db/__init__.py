import logging
from sqlalchemy.orm import Session

from app.db.base import Base, engine

def init_db(db: Session) -> None:
    """Inicializa la base de datos creando todas las tablas"""
    # Crea todas las tablas
    Base.metadata.create_all(bind=engine)
    logging.info("Base de datos inicializada")