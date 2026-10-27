from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import select

from app.core.auth import DB, Context, CurrentUser
from app.core.config import get_settings
from app.models import Curriculum, Lesson, Membership, School
from app.schemas import (
    CurriculumCreate,
    CurriculumRead,
    LessonCreate,
    LessonRead,
    MembershipRead,
    MeRead,
)

router = APIRouter()


@router.get("/me", response_model=MeRead, tags=["identity"])
def me(db: DB, user: CurrentUser):
    rows = db.execute(
        select(Membership, School).join(School).where(Membership.user_id == user.id)
    ).all()
    settings = get_settings()
    return MeRead(
        name=user.name,
        auth_mode=settings.auth_mode,
        ai_provider=settings.ai_provider,
        schools=[MembershipRead(school_id=s.id, school_name=s.name, role=m.role) for m, s in rows],
    )


@router.get("/curricula", response_model=list[CurriculumRead], tags=["curriculum"])
def curricula(db: DB, ctx: Context, limit: int = Query(100, ge=1, le=200)):
    return db.scalars(
        select(Curriculum)
        .where(Curriculum.school_id == ctx.school.id)
        .order_by(Curriculum.title)
        .limit(limit)
    ).all()


@router.post("/curricula", response_model=CurriculumRead, status_code=201, tags=["curriculum"])
def create_curriculum(body: CurriculumCreate, db: DB, ctx: Context):
    if ctx.role != "admin":
        raise HTTPException(403, "Only school administrators can create curriculum records")
    record = Curriculum(**body.model_dump(), school_id=ctx.school.id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/lessons", response_model=list[LessonRead], tags=["lessons"])
def lessons(db: DB, ctx: Context, limit: int = Query(100, ge=1, le=200)):
    return db.scalars(
        select(Lesson)
        .where(Lesson.school_id == ctx.school.id, Lesson.author_id == ctx.user.id)
        .order_by(Lesson.title)
        .limit(limit)
    ).all()


@router.post("/lessons", response_model=LessonRead, status_code=201, tags=["lessons"])
def create_lesson(body: LessonCreate, db: DB, ctx: Context):
    if body.curriculum_id:
        curriculum = db.scalar(
            select(Curriculum).where(
                Curriculum.id == body.curriculum_id, Curriculum.school_id == ctx.school.id
            )
        )
        if not curriculum:
            raise HTTPException(404, "Curriculum not found")
    record = Lesson(**body.model_dump(), school_id=ctx.school.id, author_id=ctx.user.id)
    db.add(record)
    db.commit()
    db.refresh(record)
    return record
