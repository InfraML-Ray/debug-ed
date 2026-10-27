from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi import HTTPException
from pydantic import ValidationError

from app.core.auth import verify_token
from app.core.config import Settings, get_settings


def test_production_rejects_demo_authentication():
    with pytest.raises(ValidationError, match="Demo authentication"):
        Settings(_env_file=None, app_env="production", auth_mode="demo")


def test_cognito_requires_configuration():
    with pytest.raises(ValidationError, match="Configure Cognito"):
        Settings(_env_file=None, auth_mode="cognito", cognito_client_id="")


def test_openrouter_requires_explicit_credentials_and_model():
    with pytest.raises(ValidationError, match="OpenRouter requires"):
        Settings(_env_file=None, auth_mode="demo", ai_provider="openrouter", openrouter_model="")


@pytest.mark.parametrize(
    "change",
    [
        {},
        {"token_use": "id"},
        {"client_id": "other-app"},
        {"iss": "https://wrong-issuer.test"},
        {"exp": 1},
        {"signature": "wrong"},
    ],
)
def test_signed_cognito_access_tokens_are_validated(monkeypatch, change):
    monkeypatch.setenv("COGNITO_REGION", "eu-west-1")
    monkeypatch.setenv("COGNITO_USER_POOL_ID", "pool")
    monkeypatch.setenv("COGNITO_CLIENT_ID", "expected-client")
    get_settings.cache_clear()
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    claims = {
        "sub": "teacher-sub",
        "iss": get_settings().cognito_issuer,
        "client_id": "expected-client",
        "token_use": "access",
        "iat": datetime.now(UTC),
        "exp": datetime.now(UTC) + timedelta(minutes=5),
    }
    claims.update({k: v for k, v in change.items() if k != "signature"})
    signing_key = (
        rsa.generate_private_key(public_exponent=65537, key_size=2048)
        if "signature" in change
        else key
    )
    token = jwt.encode(claims, signing_key, algorithm="RS256", headers={"kid": "test-key"})
    mock_jwks = SimpleNamespace(
        get_signing_key_from_jwt=lambda _: SimpleNamespace(key=key.public_key())
    )
    with patch("app.core.auth.jwks_client", return_value=mock_jwks):
        if change:
            with pytest.raises(HTTPException) as exc:
                verify_token(token)
            assert exc.value.status_code == 401
        else:
            assert verify_token(token) == "teacher-sub"
    get_settings.cache_clear()


def test_cognito_rejects_anonymous_requests(client, monkeypatch):
    for name, value in {
        "AUTH_MODE": "cognito",
        "COGNITO_REGION": "eu-west-1",
        "COGNITO_USER_POOL_ID": "pool",
        "COGNITO_CLIENT_ID": "app",
    }.items():
        monkeypatch.setenv(name, value)
    get_settings.cache_clear()
    assert client.get("/api/v1/me").status_code == 401
    get_settings.cache_clear()
