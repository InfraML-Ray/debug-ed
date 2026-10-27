# Debug Ed

A starter repository for a school LMS: curriculum, lesson planning, and a teacher AI companion.

This is a runnable foundation for the team, with a small working example of each area. It is not a finished LMS. The working name is **Debug Ed**; no GitHub repository or AWS resources are created by setup.

## What “boilerplate repo” means here

A repository is the project folder tracked by Git. Boilerplate is the initial wiring your team would otherwise repeat: application structure, configuration, database migrations, API conventions, authentication boundaries, tests, and development commands.

This is a **monorepo**: frontend and backend live in the same Git repository. They run as separate applications and can deploy independently.

| Part | Choice | Reason |
| --- | --- | --- |
| Frontend | Next.js App Router, React, TypeScript | Matches your team's frontend choice; responsive browser UI |
| API | FastAPI, Pydantic | Python with typed request validation and interactive API docs |
| Database | PostgreSQL | Relational school, membership, curriculum, and lesson records |
| Local fallback | SQLite | Run the starter without installing or starting a database server |
| Database access | SQLAlchemy | Explicit models and queries shared across local and PostgreSQL environments |
| Schema changes | Alembic | Versioned, reviewable migrations |
| Sign-in target | Amazon Cognito, OIDC authorization code + PKCE | Managed identity on AWS; no password database in this app |
| AI | Provider interface + OpenRouter HTTP adapter | Keep model choice configurable and API keys on the backend |
| Checks | pytest, Ruff, TypeScript, ESLint, GitHub Actions | Catch regressions and mismatched API types |
| AWS direction | ECS/Fargate, RDS PostgreSQL, Cognito | Container-based path; see [AWS notes](docs/aws.md) |

Framework choice is a proposed starting point, not an existing team decision. PostgreSQL is the target for shared development and hosting; SQLite is only a convenience for local work.

## Start locally

Requirements: **Node.js 24 LTS**, npm, **Python 3.12+**, and Make. Docker is optional. On Windows use WSL for these commands.

```sh
# From the repository root:
make setup
```

If Python has a different executable path:

```sh
make setup PYTHON=/path/to/python3.12
```

Setup creates an isolated Python environment, installs locked dependencies, copies example environment files only if they are missing, applies migrations, and seeds local demo data. It preserves existing environment files. Seeding is for local development only.

Open two terminals in the repository:

```sh
# Terminal 1: Python API
make api
```

```sh
# Terminal 2: Next.js frontend
make web
```

Open [the workspace](http://127.0.0.1:3000), [interactive API docs](http://127.0.0.1:8000/docs), or [readiness check](http://127.0.0.1:8000/health/ready).

Select the required Node/Python versions before setup; a system Python 3.9 installation is too old for this project. `.venv` and `node_modules` are ignored by Git and are recreated on each computer. Setup keeps Python dependencies isolated from your global installation.

### Try the working flow

1. Open **Curriculum** and inspect the seeded learning objectives, or add a curriculum record as the demo school administrator.
2. Open **AI companion**, select a curriculum, and send a message.
3. The default reply is explicitly labelled as a fixed demo example; no paid AI request is made.
4. Choose **Use as a lesson draft**, edit it, add a title, and save it in **Lesson planner**.
5. Reload the page: curriculum and lesson drafts remain in the local database. Chat turns are stored server-side, but a conversation browser/reopen UI is not included yet.

The visual interface is a starter for testing the wiring, not an implementation of your team's Figma designs.

## Use PostgreSQL locally

Start Docker Desktop, then:

```sh
make db-up
```

Set this in `apps/api/.env`:

```dotenv
DATABASE_URL=postgresql+psycopg://debug_ed:local-development-only@127.0.0.1:5432/debug_ed
```

Then run `make migrate`, `make seed`, and restart the API. SQLite and PostgreSQL have separate data; changing the URL does not transfer records.

Alternatively, run all three applications in local-demo containers:

```sh
cp -n apps/api/.env.example apps/api/.env
docker compose up --build
```

Stop host-run servers first to free ports 3000/8000. Compose deliberately runs local demo authentication and binds published ports to loopback. It is not an AWS production deployment. `docker compose down` stops containers and preserves the database volume; deleting that volume deletes its data.

## Connect OpenRouter

In `apps/api/.env` set:

```dotenv
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=your-key
OPENROUTER_MODEL=provider/model-id-from-your-account
```

Restart the API and reload the frontend. The adapter calls OpenRouter's chat completions endpoint with bounded input history, an output-token cap, a timeout, and no automatic retries. Choose a model available to your account and configure its spending limit there. No model or paid request is selected implicitly.

Keys remain on the API server. Never put them in a `NEXT_PUBLIC_` variable, frontend source, Git, or a shared screenshot. Frontend variables with that prefix are public and bundled at build time.

With a selected curriculum, the API supplies its title and objectives as context after checking school membership. The UI lists **context supplied**, not verified citations. With no curriculum selected, chat is general teaching assistance. Full document ingestion, embeddings, vector search, and source-level citations are not implemented. See [the AI guide](docs/companion.md).

## Repo map

```text
apps/
  web/                       Next.js frontend
    src/app/                 Workspace, sign-in callback, styling
    src/lib/api.ts           Typed API request helper
    src/lib/auth.ts          Browser OIDC/PKCE sign-in
    src/lib/api-schema.d.ts  Generated from FastAPI's OpenAPI schema
  api/                       FastAPI backend
    app/core/                Settings, database sessions, authentication
    app/models.py            School, membership, curriculum, lesson, chat tables
    app/routes/              Versioned HTTP endpoints
    app/companion/           AI provider and curriculum-retrieval boundaries
    alembic/                 Schema migrations
    tests/                   Behaviour, access-control, and authentication tests
docs/                        Architecture, AI, AWS, and team handoff notes
scripts/                     Setup and API type generation
.github/workflows/ci.yml     SQLite/PostgreSQL API checks and frontend build
compose.yaml                 Local PostgreSQL + optional full-stack containers
```

Your main starting points for AI work are `apps/api/app/companion/providers.py`, `apps/api/app/companion/retrieval.py`, and `apps/api/app/routes/companion.py`.

## Development commands

| Command | Purpose |
| --- | --- |
| `make api` / `make web` | Start development servers |
| `make check` | API lint/tests; frontend typecheck/lint/build |
| `make test` | Run backend behaviour tests with isolated SQLite databases |
| `make migrate` | Apply database migrations |
| `make seed` | Add the local demo school and teacher if missing |
| `make types` | Regenerate TypeScript types after changing API schemas |
| `make db-up` / `make db-down` | Start/stop local PostgreSQL |

For a schema change, edit `app/models.py`, then from `apps/api`:

```sh
.venv/bin/alembic revision --autogenerate -m "Describe the change"
# Review the generated migration before applying it.
.venv/bin/alembic upgrade head
.venv/bin/alembic check
```

Do not change an existing migration once it has been shared/applied; add a new one. Do not use `create_all()` to evolve shared databases.

`package-lock.json` locks JavaScript dependencies. `apps/api/requirements.lock` constrains Python dependency versions for repeatable installation. Intentional dependency updates should regenerate the lock, pass checks, and be reviewed together with the manifest change. To refresh Python constraints after an intentional update, run `.venv/bin/pip freeze --exclude debug-ed-api > requirements.lock` inside `apps/api`.

## Before a school pilot

Connect and test real Cognito sign-in, provision real school memberships, implement the agreed lesson/curriculum workflows, and review the AI scope with the team. Configure server-side usage limits, data retention, logging/monitoring, backups, and the AWS infrastructure described in [docs/aws.md](docs/aws.md). Local demo authentication impersonates a shared account, and `APP_ENV=production` rejects it.

See [team handoff and remaining decisions](docs/handoff.md). No license has been assigned; choose one with the team before distributing the repository.

## Reference documentation

[Next.js setup](https://nextjs.org/docs/app/getting-started/installation), [FastAPI containers](https://fastapi.tiangolo.com/deployment/docker/), [SQLAlchemy](https://docs.sqlalchemy.org/en/21/orm/quickstart.html), [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html), [OpenRouter](https://openrouter.ai/docs/api_reference/overview), [Cognito token verification](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html).
