from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Declarative base for MzPoliShine ORM models."""

    pass


__all__ = ["Base"]
