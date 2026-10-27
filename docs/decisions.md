# Project decisions

## Confirmed

- Deliver a boilerplate repository and structure, not the first product iteration.
- Python backend and Next.js/TypeScript frontend.
- Browser-first; native mobile apps are not part of this scaffold.
- Future feature areas: curriculum, lesson planner, and AI companion.
- One school for the eventual first iteration, with multiple schools/teachers later.
- Fresh accounts and application data; no migration from the old app is required.
- AWS hosting target.
- Your primary feature area will be the AI companion.
- Repository name: `debug-ed`, under the `InfraML-Ray` personal GitHub account, private for team review.

## Boilerplate defaults

- One Git repository with `apps/web` and `apps/api`.
- FastAPI, SQLAlchemy, Alembic, PostgreSQL driver, local SQLite option.
- Versioned API routing, environment examples, dependency locks, checks, Dockerfiles, and CI.
- Feature directories are placeholders only.

## Undecided

- Authentication provider, sessions, roles, and tenancy schema.
- AI provider/model and what the meeting's “open route” reference meant.
- AI retrieval, document ingestion, and exact feature behaviour.
- Specific AWS services, region, and resource reuse.
- Long-term GitHub organisation ownership and license. “Debug Ed” is the working product name.

The old repo is background context. Its Better Auth, Bedrock, and EC2 choices are not commitments for this rebuild. The earlier functional demo is recoverable in Git history; current source is restricted to the boilerplate scope.
