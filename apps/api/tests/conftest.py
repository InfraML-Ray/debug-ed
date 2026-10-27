import os
from pathlib import Path

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from alembic import command

os.environ["APP_ENV"] = "test"
os.environ["AUTH_MODE"] = "demo"
os.environ["AI_PROVIDER"] = "demo"

from app.core.config import get_settings  # noqa: E402
from app.core.database import get_engine  # noqa: E402
from app.main import create_app  # noqa: E402
from app.seed import seed  # noqa: E402


@pytest.fixture
def database(monkeypatch, tmp_path):
    # CI can run the same isolation tests on PostgreSQL; local tests need no service.
    url = os.environ.get("TEST_DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("DATABASE_URL", url)
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("AUTH_MODE", "demo")
    monkeypatch.setenv("AI_PROVIDER", "demo")
    get_settings.cache_clear()
    get_engine.cache_clear()
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    command.upgrade(config, "head")
    seed()
    yield
    command.downgrade(config, "base")
    get_engine().dispose()
    get_engine.cache_clear()
    get_settings.cache_clear()


@pytest.fixture
def db(database):
    with Session(get_engine()) as session:
        yield session


@pytest.fixture
def app(database):
    return create_app()


@pytest.fixture
def client(app):
    with TestClient(app) as client:
        yield client
