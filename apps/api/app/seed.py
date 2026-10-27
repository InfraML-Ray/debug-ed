"""Idempotent, local-only demo data. Run after Alembic migrations."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.auth import DEMO_SUBJECT
from app.core.config import get_settings
from app.core.database import get_engine
from app.models import Curriculum, Lesson, Membership, School, User

DEMO_SCHOOL_ID = "00000000-0000-4000-8000-000000000001"


def seed():
    if get_settings().app_env not in {"local", "test"}:
        raise RuntimeError("Demo seeding is only allowed locally")
    with Session(get_engine()) as db:
        if db.scalar(select(User).where(User.subject == DEMO_SUBJECT)):
            return
        school = School(id=DEMO_SCHOOL_ID, name="Maple Grove School · Demo")
        teacher = User(subject=DEMO_SUBJECT, name="Alex Morgan")
        db.add_all([school, teacher])
        db.flush()
        db.add(Membership(user_id=teacher.id, school_id=school.id, role="admin"))
        curriculum = Curriculum(
            school_id=school.id,
            title="Living things & their habitats",
            subject="Science",
            grade="Year 4",
            objectives="Identify living things and group them by habitat. "
            "Explain how changing environments affect plants and animals. "
            "Use observations to support a simple explanation.",
        )
        db.add(curriculum)
        db.flush()
        db.add(
            Lesson(
                school_id=school.id,
                author_id=teacher.id,
                curriculum_id=curriculum.id,
                title="Exploring our local habitats",
                duration_minutes=40,
                content="Learning objective: identify features of a habitat.\n\n"
                "Starter (5 min): describe a place where an animal lives.\n"
                "Explore (15 min): compare a pond and a woodland habitat.\n"
                "Practise (15 min): sort living things by habitat in pairs.\n"
                "Exit ticket (5 min): explain one adaptation using evidence.",
            )
        )
        db.commit()


if __name__ == "__main__":
    seed()
    print("Local demo data is ready.")
