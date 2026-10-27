from sqlalchemy import func, select

from app.companion.providers import ProviderUnavailable
from app.models import Conversation, Message, User
from app.routes.companion import get_provider


class RecordingProvider:
    def __init__(self):
        self.messages = []

    def complete(self, messages):
        self.messages = messages
        return "A grounded lesson draft"


def test_demo_chat_is_labelled_and_persisted(client, db):
    result = client.post("/api/v1/companion/chat", json={"message": "Help me plan"})
    assert result.status_code == 200
    assert result.json()["provider"] == "demo"
    assert "no AI model was called" in result.json()["answer"]
    assert result.json()["sources"] == []
    assert db.scalar(select(func.count()).select_from(Message)) == 2


def test_context_and_history_are_forwarded(client, app):
    provider = RecordingProvider()
    app.dependency_overrides[get_provider] = lambda: provider
    curriculum = client.get("/api/v1/curricula").json()[0]
    first = client.post(
        "/api/v1/companion/chat",
        json={
            "message": "Draft a lesson",
            "curriculum_id": curriculum["id"],
        },
    ).json()
    assert first["sources"][0]["id"] == curriculum["id"]
    assert curriculum["objectives"] in provider.messages[1]["content"]
    second = client.post(
        "/api/v1/companion/chat",
        json={
            "message": "Make it shorter",
            "conversation_id": first["conversation_id"],
            "curriculum_id": curriculum["id"],
        },
    )
    assert second.status_code == 200
    assert any(
        m["role"] == "assistant" and m["content"] == "A grounded lesson draft"
        for m in provider.messages
    )
    assert provider.messages[-1]["content"] == "Make it shorter"


def test_other_users_conversation_is_inaccessible(client, db):
    school_id = client.get("/api/v1/me").json()["schools"][0]["school_id"]
    user = User(subject="other-user", name="Other user")
    db.add(user)
    db.flush()
    conversation = Conversation(user_id=user.id, school_id=school_id)
    db.add(conversation)
    db.commit()
    assert (
        client.post(
            "/api/v1/companion/chat",
            json={
                "message": "Read private chat",
                "conversation_id": conversation.id,
            },
        ).status_code
        == 404
    )


def test_provider_failure_does_not_save_partial_chat(client, app, db):
    class UnavailableProvider:
        def complete(self, messages):
            raise ProviderUnavailable("The AI provider is unavailable. Please try again.")

    app.dependency_overrides[get_provider] = lambda: UnavailableProvider()
    assert client.post("/api/v1/companion/chat", json={"message": "Hello"}).status_code == 503
    assert db.scalar(select(func.count()).select_from(Conversation)) == 0
    assert db.scalar(select(func.count()).select_from(Message)) == 0


def test_empty_or_oversized_prompt_is_rejected(client):
    for prompt in [" ", "x" * 6001]:
        assert client.post("/api/v1/companion/chat", json={"message": prompt}).status_code == 422
