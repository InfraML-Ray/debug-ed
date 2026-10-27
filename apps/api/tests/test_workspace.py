from sqlalchemy import func, select

from app.models import Conversation, Curriculum, Lesson, Membership, School, User


def foreign_school(db):
    school = School(name="Other school")
    db.add(school)
    db.flush()
    curriculum = Curriculum(
        school_id=school.id,
        title="Private curriculum",
        subject="Math",
        grade="5",
        objectives="Confidential learning objectives",
    )
    db.add(curriculum)
    db.commit()
    return school, curriculum


def test_boot_and_seed_are_usable(client):
    assert client.get("/health/live").status_code == 200
    assert client.get("/health/ready").status_code == 200
    assert client.get("/api/v1/me").json()["schools"][0]["role"] == "admin"
    assert len(client.get("/api/v1/curricula").json()) == 1
    assert len(client.get("/api/v1/lessons").json()) == 1


def test_school_header_cannot_grant_access(client, db):
    school, _ = foreign_school(db)
    for path in ["/curricula", "/lessons"]:
        assert client.get(f"/api/v1{path}", headers={"X-School-ID": school.id}).status_code == 403


def test_foreign_curriculum_cannot_be_attached_to_lesson(client, db):
    _, curriculum = foreign_school(db)
    response = client.post(
        "/api/v1/lessons",
        json={
            "title": "Attempt",
            "content": "Test",
            "curriculum_id": curriculum.id,
        },
    )
    assert response.status_code == 404
    assert db.scalar(select(func.count()).select_from(Lesson)) == 1


def test_admin_can_create_curriculum_and_author_can_save_lesson(client):
    curriculum = client.post(
        "/api/v1/curricula",
        json={
            "title": "Fractions",
            "subject": "Math",
            "grade": "4",
            "objectives": "Compare fractions",
        },
    )
    assert curriculum.status_code == 201
    lesson = client.post(
        "/api/v1/lessons",
        json={
            "title": "Fraction strips",
            "content": "Compare thirds and quarters",
            "curriculum_id": curriculum.json()["id"],
            "duration_minutes": 30,
        },
    )
    assert lesson.status_code == 201
    assert lesson.json()["id"] in [row["id"] for row in client.get("/api/v1/lessons").json()]


def test_teacher_cannot_create_school_curriculum(client, db):
    membership = db.scalar(select(Membership))
    membership.role = "teacher"
    db.commit()
    assert (
        client.post(
            "/api/v1/curricula",
            json={
                "title": "Fractions",
                "subject": "Math",
                "grade": "4",
                "objectives": "Compare fractions",
            },
        ).status_code
        == 403
    )


def test_lessons_are_private_to_author(client, db):
    school_id = client.get("/api/v1/me").json()["schools"][0]["school_id"]
    other = User(subject="another-teacher", name="Another teacher")
    db.add(other)
    db.flush()
    db.add(
        Lesson(school_id=school_id, author_id=other.id, title="Private draft", content="Private")
    )
    db.commit()
    assert all(row["title"] != "Private draft" for row in client.get("/api/v1/lessons").json())


def test_invalid_lesson_is_rejected(client):
    for body in [
        {"title": " ", "content": "Test"},
        {"title": "Test", "content": "Test", "duration_minutes": 0},
    ]:
        assert client.post("/api/v1/lessons", json=body).status_code == 422


def test_chat_cannot_read_another_school_curriculum(client, db):
    _, curriculum = foreign_school(db)
    assert (
        client.post(
            "/api/v1/companion/chat",
            json={
                "message": "Explain it",
                "curriculum_id": curriculum.id,
            },
        ).status_code
        == 404
    )
    assert db.scalar(select(func.count()).select_from(Conversation)) == 0


def test_multiple_memberships_require_selection_and_keep_records_scoped(client, db):
    primary_school = client.get("/api/v1/me").json()["schools"][0]["school_id"]
    other_school, other_curriculum = foreign_school(db)
    user = db.scalar(select(User).where(User.subject == "local-demo-teacher"))
    db.add(Membership(user_id=user.id, school_id=other_school.id, role="teacher"))
    db.commit()
    assert client.get("/api/v1/curricula").status_code == 400
    primary = client.get("/api/v1/curricula", headers={"X-School-ID": primary_school})
    other = client.get("/api/v1/curricula", headers={"X-School-ID": other_school.id})
    assert all(row["id"] != other_curriculum.id for row in primary.json())
    assert [row["id"] for row in other.json()] == [other_curriculum.id]
