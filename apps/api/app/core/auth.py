from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.models import Membership, School, User

DEMO_SUBJECT = "local-demo-teacher"
bearer = HTTPBearer(auto_error=False)
DB = Annotated[Session, Depends(get_db)]


@dataclass
class SchoolContext:
    user: User
    school: School
    role: str


@lru_cache
def jwks_client():
    return jwt.PyJWKClient(f"{get_settings().cognito_issuer}/.well-known/jwks.json", timeout=5)


def verify_token(token: str) -> str:
    settings = get_settings()
    try:
        key = jwks_client().get_signing_key_from_jwt(token)
        claims = jwt.decode(
            token,
            key.key,
            algorithms=["RS256"],
            issuer=settings.cognito_issuer,
            options={"verify_aud": False, "require": ["exp", "iat", "sub", "iss"]},
        )
        if claims.get("token_use") != "access":
            raise jwt.InvalidTokenError("Expected access token")
        if claims.get("client_id") != settings.cognito_client_id:
            raise jwt.InvalidTokenError("Wrong client")
        return claims["sub"]
    except jwt.PyJWTError as exc:
        raise HTTPException(401, "Invalid or expired access token") from exc


def get_user(
    db: DB,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
) -> User:
    settings = get_settings()
    if settings.auth_mode == "demo":
        subject = DEMO_SUBJECT
    elif credentials:
        subject = verify_token(credentials.credentials)
    else:
        raise HTTPException(401, "Sign in to continue")
    user = db.scalar(select(User).where(User.subject == subject))
    if not user:
        raise HTTPException(403, "Your school administrator must provision your membership")
    return user


CurrentUser = Annotated[User, Depends(get_user)]


def get_context(
    db: DB, user: CurrentUser, x_school_id: Annotated[str | None, Header()] = None
) -> SchoolContext:
    query = select(Membership).where(Membership.user_id == user.id)
    if x_school_id:
        query = query.where(Membership.school_id == x_school_id)
    memberships = db.scalars(query).all()
    if not memberships:
        raise HTTPException(403, "No access to this school")
    if len(memberships) != 1:
        raise HTTPException(400, "Select a school with X-School-ID")
    membership = memberships[0]
    if membership.role not in {"teacher", "admin"}:
        raise HTTPException(403, "A teacher or administrator role is required")
    school = db.get(School, membership.school_id)
    return SchoolContext(user=user, school=school, role=membership.role)


Context = Annotated[SchoolContext, Depends(get_context)]
