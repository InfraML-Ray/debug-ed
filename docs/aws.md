# AWS deployment direction

These are proposed deployment choices. Infrastructure has not been provisioned, container builds have not been run on the original workstation because the Docker daemon was stopped, and no AWS credentials are required for local demo development.

## Initial layout

- Run the Next.js server and FastAPI as separate ECS services on Fargate, with images in ECR.
- Put an HTTPS Application Load Balancer in front, routing the frontend and API to their respective target groups. If routing `/api/*` to Python, `/api/v1/...` must reach Python unchanged. Set `NEXT_PUBLIC_API_URL` to the public origin without `/api/v1`, because the client adds that path.
- Use RDS PostgreSQL in private subnets. Set `DATABASE_URL` with the `postgresql+psycopg://` driver and configure TLS, for example `?sslmode=require`.
- Use Cognito user pools for identity, Secrets Manager for API/database secrets, and CloudWatch for operational logs and metrics.
- Add private S3 storage and an ingestion worker only when document uploads become part of scope.

Container definitions are included in `apps/web/Dockerfile` and `apps/api/Dockerfile`. Build them from the repo root. The local Compose file is intentionally a demo configuration, with loopback ports and local-only credentials; do not reuse it as a production configuration.

Review AWS region, network design, expected load, cost, and your organisation's existing infrastructure before choosing task sizing or high availability. There is no Terraform/CDK stack yet because those account-specific decisions are open.

## Cognito setup

1. Create a user pool and managed login domain.
2. Create a **public app client without a client secret**. Enable authorization code grant and `openid email profile` scopes. The browser library performs PKCE.
3. Register exact callback URLs, e.g. `http://localhost:3000/auth/callback` for local sign-in and `https://your-domain/auth/callback` for production. Use the matching origin when opening the frontend; `localhost` and `127.0.0.1` are different callback URLs.
4. Register exact sign-out destinations, e.g. `http://localhost:3000` and `https://your-domain`.
5. Disable unapproved self-registration for a school-managed pilot. App registration alone never grants a school membership in this backend.
6. Set API configuration:

```dotenv
APP_ENV=production
AUTH_MODE=cognito
DATABASE_URL=postgresql+psycopg://...
CORS_ORIGINS=["https://your-domain"]
COGNITO_REGION=your-region
COGNITO_USER_POOL_ID=your-pool-id
COGNITO_CLIENT_ID=your-public-app-client-id
AI_PROVIDER=openrouter
OPENROUTER_API_KEY=from-secrets-manager
OPENROUTER_MODEL=your-reviewed-model-id
```

7. Set frontend **build-time** variables:

```dotenv
NEXT_PUBLIC_API_URL=https://your-domain
NEXT_PUBLIC_AUTH_MODE=cognito
NEXT_PUBLIC_COGNITO_AUTHORITY=https://cognito-idp.your-region.amazonaws.com/your-pool-id
NEXT_PUBLIC_COGNITO_CLIENT_ID=your-public-app-client-id
NEXT_PUBLIC_COGNITO_DOMAIN=https://your-prefix.auth.your-region.amazoncognito.com
```

Pass these as Docker build arguments. Changing runtime task environment variables does not update values already compiled into a Next.js client bundle; rebuild the frontend image.

8. Apply migrations in a one-off release task, then provision the initial administrator using a verified Cognito subject:

```sh
python -m app.provision --school-name "Example School" --subject "verified-cognito-sub" --name "School Admin" --role admin
```

The command prints a school ID. Add subsequent teachers using that ID:

```sh
python -m app.provision --school-id "school-uuid" --school-name "Example School" --subject "another-verified-sub" --name "Teacher Name" --role teacher
```

Use a trusted administrator/release environment with the target database configuration. The provisioning CLI is an operational tool; there is no public enrolment endpoint. Do not seed demo users in production.

## Authentication details and limitations

The browser uses `oidc-client-ts` for OIDC authorization code + PKCE. Tokens are kept in session storage for this starter. The backend verifies access tokens against cached Cognito signing keys and checks the expected issuer, app client, token purpose, and expiry. It does not accept ID tokens as API access tokens. School roles are resolved from the database, not user-provided headers or editable profile claims.

Automatic silent refresh is disabled; the starter asks the teacher to sign in again after expiry. Sign-out removes the local token and ends the Cognito browser session. Offline JWT verification cannot detect token revocation before expiry; use short access-token lifetimes and evaluate revocation requirements. A server-managed session/BFF is an alternative if the team wants to keep all tokens out of browser storage.

Real Cognito sign-in has not been tested against a provisioned user pool. Verify login, callback matching, expired tokens, logout, unprovisioned users, and two different school memberships in the staging environment.

## Release checklist

- Run the checked-in CI, including the PostgreSQL test matrix and schema drift check.
- Build and smoke-test both containers against PostgreSQL; run migrations once per release, not on every production web-worker startup.
- Enable HTTPS, exact CORS origins, least-privilege IAM/security groups, RDS backups, and secret injection.
- Configure provider spending limits plus server-side school/user quotas and concurrency controls before allowing real AI traffic.
- Add request IDs, redacted operational logs, metrics, alerts, retention/deletion procedures, and a restore test.
- Agree on CSP/security headers, browser token storage, school role permissions, and data-processing rules with the team.

References: [ECS/Fargate](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/Welcome.html), [RDS PostgreSQL](https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/CHAP_PostgreSQL.html), [Cognito authorization/PKCE](https://docs.aws.amazon.com/cognito/latest/developerguide/authorization-endpoint.html), [Cognito token validation](https://docs.aws.amazon.com/cognito/latest/developerguide/amazon-cognito-user-pools-using-tokens-verifying-a-jwt.html).
