PYTHON ?= python3.12
API = apps/api

.PHONY: setup api web check test migrate seed db-up db-down types

setup:
	$(PYTHON) scripts/setup.py

api:
	cd $(API) && .venv/bin/uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

web:
	npm run dev

check:
	cd $(API) && .venv/bin/ruff check app tests alembic
	cd $(API) && .venv/bin/pytest -q
	npm run typecheck
	npm run lint
	npm run build

test:
	cd $(API) && .venv/bin/pytest -q

migrate:
	cd $(API) && .venv/bin/alembic upgrade head

seed:
	cd $(API) && .venv/bin/python -m app.seed

db-up:
	docker compose up -d db

db-down:
	docker compose stop db

types:
	npm run api:types
