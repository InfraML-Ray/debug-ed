# Structure conventions

This is a monorepo containing two applications, not an implemented LMS.

- `apps/web` owns browser presentation. `src/app` is routing/layout; `src/features` groups future domain UI; `src/components` holds genuinely shared UI.
- `apps/api` owns future application rules and persistence. `app/api/v1` composes HTTP routers; `app/modules` groups future feature implementations.
- `app/core` holds shared settings; `app/db` holds SQLAlchemy base/session plumbing. No business models or initial migrations are defined.
- `docs` captures decisions and conventions. `scripts` contains local developer tooling.

## Future module convention

When a feature needs implementation, add only the files it needs:

```text
modules/<feature>/
  router.py      # HTTP endpoints
  schemas.py     # Request/response validation
  service.py     # Business rules
  models.py      # Persistence, when needed
```

Reuse `app/db/base.py` for models and `app/db/session.py` for request-scoped database sessions. Import models into Alembic's environment before generating migrations. Keep external provider calls inside the relevant module's adapter layer once a provider is selected.

## Existing behaviour

The frontend serves one static placeholder page. The API exposes a health endpoint and generated OpenAPI docs. An API boot/health smoke test verifies test wiring. No feature routes, school-access logic, authentication, AI calls, or demo records are included. Add access control and meaningful feature tests with future implementation.

Dockerfiles are build scaffolding, and Compose is local development configuration. Choose AWS services and write deployment infrastructure after the team agrees on that setup.
