# AI companion development guide

The companion's scope is deliberately small while product requirements are open. Its current responsibility is to assemble teacher context and bounded conversation history, call a provider, and persist a successful exchange.

## Where to work

| File | Responsibility |
| --- | --- |
| `apps/api/app/companion/providers.py` | Provider interface, fixed demo provider, and OpenRouter adapter |
| `apps/api/app/companion/retrieval.py` | Tenant-scoped context retrieval boundary |
| `apps/api/app/routes/companion.py` | Prompt assembly, conversation ownership, orchestration, persistence |
| `apps/api/app/schemas.py` | Public chat request/response contract |
| `apps/api/tests/test_companion.py` | History, ownership, failure, and context behaviour |

The production AI provider is **undecided**. OpenRouter is available as an optional adapter, but the meeting's “open route” reference has not been clarified. The previous app documented Amazon Bedrock; that does not commit the rebuild to Bedrock or OpenRouter. Local demo replies remain the default and make no external model calls.

Once the team chooses a provider, configure the existing OpenRouter adapter or add another implementation of `ChatProvider` and extend the provider settings/factory. A Bedrock adapter is not implemented yet. Keep provider-specific authentication and request formatting in the adapter, with prompts, school-scoped context, and conversation ownership in the application layer.

## Current request

```http
POST /api/v1/companion/chat
Authorization: Bearer <Cognito access token>
X-School-ID: <school UUID>
Content-Type: application/json

{
  "message": "Help me draft a 40-minute lesson",
  "curriculum_id": "optional curriculum UUID",
  "conversation_id": "optional existing conversation UUID"
}
```

The school and user come from authenticated membership, not request JSON. Existing conversations require both owner and school matches. Failed provider calls roll back rather than saving incomplete exchanges. The input message is limited to 6,000 characters; at most 12 prior turns of up to 6,000 characters each are included. Output tokens are capped by configuration. The selected curriculum contributes up to 12,000 characters.

The response returns the conversation ID, answer, provider mode, and supplied curriculum source labels. These labels describe context supplied to the model; they do not prove that generated claims are supported by it. Demo replies are fixed examples and do not perform reasoning over the selected curriculum.

The companion currently drafts text only. It cannot execute tools, publish curriculum, change records, browse the web, or issue arbitrary database queries. The teacher explicitly reviews and saves lesson drafts through the normal lesson API.

## Adding document retrieval later

Keep the same `Retriever` boundary, and agree on the following before implementing ingestion:

1. Sources and permissions: school documents, teacher-owned documents, curriculum records, or approved public sources.
2. Formats and ingestion: PDF/DOCX/text, scanned documents requiring OCR, size limits, duplicate handling, versioning.
3. Storage: private S3 objects, ingestion metadata and job state in PostgreSQL, and a worker for extraction/chunking.
4. Search: embeddings and a vector index if search quality requires them. PostgreSQL with pgvector is an option to evaluate, not an installed dependency.
5. Access: enforce school/user scopes in the retrieval query, source metadata, and object access; never retrieve broadly and rely on the prompt to filter.
6. Answers: source excerpts, document/page references, and honest “not found” behaviour.

Do not add a framework, vector database, queue, or agents until those requirements justify the dependency.

## Evaluation and usage controls

Before real teacher use, build a small reviewed evaluation set covering lesson drafting, curriculum answers with and without supporting evidence, ambiguous questions, prompt injection in documents, age/grade appropriateness, and cross-school access. Add per-user/school quotas and concurrency limits, server-side cost/usage records, provider timeouts, and a retention policy. The existing request bounds and output cap are helpful defaults but are not a spending quota.

Do not log prompts, student information, provider keys, or full provider error responses. Decide which information may leave the school environment and which provider policies satisfy that requirement before using real school documents.
