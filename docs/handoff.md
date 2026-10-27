# Team handoff

## Agreed in this session

- Rebuild the LMS from scratch.
- Start with fresh accounts and application data; migration of previous users or school data is not required. Reuse of AWS resources has not been decided.
- One school in the first iteration; support additional schools and teachers later.
- Whole web application in this repository, with Python backend and Next.js/TypeScript frontend.
- Browser-first, responsive layouts. Mobile Figma screens do not yet imply native apps.
- Curriculum, lesson planner, and AI companion are the product areas; your primary responsibility is the companion.
- AWS hosting. The AI provider, detailed companion scope, and document retrieval are undecided.

## Proposed defaults implemented here

- FastAPI, SQLAlchemy, Alembic, PostgreSQL target, local SQLite fallback.
- Cognito sign-in integration, explicit school memberships, teacher/admin roles.
- Optional OpenRouter adapter, configurable model, clearly labelled local demo replies. OpenRouter is not a confirmed provider choice; the previous app's Bedrock integration does not determine the rebuild's provider either.
- A single Git repo, small shared API contract, CI, and independently containerised web/API services.
- “Debug Ed” as the working project name. Local repository only; no GitHub visibility or organisation choice was supplied.

## Decisions to take back to the team

1. Confirm the product/repository name and GitHub organisation, visibility, and licensing.
2. Confirm FastAPI vs an existing team preference, and the existing AWS region/infrastructure conventions.
3. Review Figma journeys and define the first complete curriculum/lesson workflow, including edit/publish/share permissions.
4. Clarify the meeting's “open route” reference and choose the AI provider/model, usage budget, and data-handling rules. Keep demo replies enabled until that decision and credentials are available.
5. Decide whether answers must use uploaded documents on day one, and collect anonymised sample curriculum material.
6. Agree on school-admin/teacher permissions, membership provisioning, pilot onboarding, and how independent teachers will fit the school boundary later.
7. Confirm pilot acceptance criteria, testing ownership, and who provisions/deploys staging.

## Suggested first team tickets

- Frontend owner: replace the starter workspace with the approved Figma screens and accessibility requirements.
- Curriculum owner: agree on curriculum hierarchy, import formats, versioning, and administrator workflows.
- Lesson owner: agree on structured lesson fields, calendar scheduling, edit history, and sharing/publishing.
- AI owner: define three core teacher tasks, curate a reviewed evaluation set, and implement measured provider/retrieval behaviour.
- Platform owner: confirm identity/hosting choices and AWS resource reuse, provision staging services, configure deployment, and test restore/monitoring. Cognito/RDS/ECS remain proposed defaults.

Use one branch per feature, keep `.env` files private, and review migrations and permission changes together. Avoid splitting this starter into multiple services until there is a concrete reason.
