from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class VacanteVista(Base):
    """Registro de cada vacante ya notificada, para no duplicar avisos."""

    __tablename__ = "vacantes_vistas"

    hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    titulo: Mapped[str] = mapped_column(String(255))
    empresa: Mapped[str] = mapped_column(String(255))
    url: Mapped[str] = mapped_column(String(500))
    fuente: Mapped[str] = mapped_column(String(50))
    fecha_detectada: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
