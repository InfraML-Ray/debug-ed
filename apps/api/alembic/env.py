from alembic import context
from app.db.base import Base
from app.db.session import get_engine

# Import future module models here so Alembic can discover their metadata.


def run_migrations_online():
    with get_engine().connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    from app.core.config import get_settings

    context.configure(
        url=get_settings().database_url, target_metadata=Base.metadata, literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()
else:
    run_migrations_online()
