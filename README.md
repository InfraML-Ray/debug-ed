# Debug Ed

Repository structure and development tooling for a future LMS. This is a scaffold: no LMS workflows, authentication integration, AI integration, business database tables, or demo data are implemented.

## Stack

- Frontend: Next.js App Router, React, TypeScript.
- Backend: Python, FastAPI, Pydantic settings.
- Database tooling: SQLAlchemy, Alembic, PostgreSQL driver; optional SQLite for local work.
- Development: npm workspaces, pytest, Ruff, ESLint, Prettier, Docker Compose, GitHub Actions.
- Hosting target: AWS. Specific AWS services are undecided.

## Structure

```text
debug-ed/
├── apps/
│   ├── web/
│   │   ├── src/
│   │   │   ├── app/                 # Next.js routes/layout; one placeholder page
│   │   │   ├── components/          # Shared UI components (empty)
│   │   │   ├── features/
│   │   │   │   ├── auth/            # Future feature placeholders
│   │   │   │   ├── curriculum/
│   │   │   │   ├── lessons/
│   │   │   │   └── companion/
│   │   │   └── lib/                 # HTTP helper and generated API types
│   │   ├── .env.example
│   │   └── Dockerfile
│   └── api/
│       ├── app/
│       │   ├── main.py             # Application factory
│       │   ├── api/v1/             # Router; health endpoint only
│       │   ├── core/               # Shared settings
│       │   ├── db/                 # SQLAlchemy base/session setup; no tables
│       │   └── modules/
│       │       ├── auth/           # Empty Python packages + scope notes
│       │       ├── curriculum/
│       │       ├── lessons/
│       │       └── companion/
│       ├── alembic/versions/       # Empty migration directory
│       ├── tests/                  # API boot/health smoke test
│       ├── .env.example
│       └── Dockerfile
├── docs/                           # Architecture conventions and decisions
├── scripts/                        # Environment setup and API type generation
├── .github/workflows/ci.yml
├── compose.yaml
├── Makefile
└── package.json                    # Root workspace commands
```

## Local setup

Requirements: Node.js 24 LTS, Python 3.12+, npm, and Make. Use WSL on Windows. Docker is optional.

From the repo root:

```sh
make setup
# Or: make setup PYTHON=/path/to/python3.12
```

Setup installs dependencies and copies example environment files if missing. It does not create business tables, seed data, or call external services.

Run `make api` and `make web` in separate terminals. Open the placeholder page at http://127.0.0.1:3000 and API docs at http://127.0.0.1:8000/docs. The only API endpoint is `GET /api/v1/health`.

Environment files, virtual environments, dependencies, and local databases are ignored by Git. Existing local environment files are preserved by setup. Frontend `NEXT_PUBLIC_` values are public build-time configuration: never put secrets there.

## Commands

| Command | Purpose |
| --- | --- |
| `make setup` | Install dependencies and create local env files |
| `make api` / `make web` | Start the two development servers |
| `make check` | Backend lint/smoke test and frontend checks/build |
| `make types` | Generate TypeScript types from FastAPI OpenAPI |
| `make db-up` / `make db-down` | Start/stop optional local PostgreSQL |
| `make migrate` | Apply future Alembic migrations; none are supplied yet |
| `npm run format` | Format frontend and JS configuration |

For PostgreSQL, start Docker Desktop, run `make db-up`, and use the example PostgreSQL URL in `apps/api/.env.example`. Alternatively, `docker compose up --build` starts the scaffold and database in containers. Docker images have not been built locally because the Docker daemon was stopped.

## Adding a feature later

Put UI components/hooks in `apps/web/src/features/<feature>`, with route pages in `src/app`. Put Python feature logic in `apps/api/app/modules/<feature>`. Add `router.py`, `schemas.py`, `service.py`, and `models.py` as needed; do not add empty layers in advance. Register routers in `app/api/v1/router.py` and import future model metadata in `alembic/env.py` before generating migrations.

Read [architecture conventions](docs/architecture.md) and [confirmed/open decisions](docs/decisions.md). AWS infrastructure is not configured. A license is still to be chosen by the team.
