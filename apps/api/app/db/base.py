from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Import this base in future module models; no application tables are defined yet."""
