import os
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from .models import Base, VacanteVista

DB_URL = "sqlite:///./data/vacantes.db"

# SQLite no crea la carpeta contenedora por sí solo; hay que asegurarla
# antes de que el engine intente abrir el archivo.
os.makedirs("data", exist_ok=True)

engine = create_engine(DB_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)


def init_db():
    """Crea las tablas si no existen. Llamar una vez al arrancar."""
    Base.metadata.create_all(engine)


def ya_vista(hash_vacante: str) -> bool:
    with SessionLocal() as session:
        existe = session.scalar(
            select(VacanteVista).where(VacanteVista.hash == hash_vacante)
        )
        return existe is not None


def guardar_vacante(vacante) -> None:
    """vacante: instancia de scrapers.base.Vacante"""
    with SessionLocal() as session:
        registro = VacanteVista(
            hash=vacante.hash_unico(),
            titulo=vacante.titulo,
            empresa=vacante.empresa,
            url=vacante.url,
            fuente=vacante.fuente,
        )
        session.merge(registro)  # merge evita error si por carrera ya existe
        session.commit()