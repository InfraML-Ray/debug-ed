"""Replace this boundary with document retrieval once ingestion and RAG are agreed."""

from dataclasses import dataclass
from typing import Protocol

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Curriculum
from app.schemas import Source


@dataclass
class RetrievedContext:
    text: str
    sources: list[Source]


class Retriever(Protocol):
    def retrieve(self, school_id: str, curriculum_id: str | None) -> RetrievedContext: ...


class CurriculumRetriever:
    def __init__(self, db: Session):
        self.db = db

    def retrieve(self, school_id: str, curriculum_id: str | None) -> RetrievedContext:
        if not curriculum_id:
            return RetrievedContext(text="No school curriculum was selected.", sources=[])
        record = self.db.scalar(
            select(Curriculum).where(
                Curriculum.id == curriculum_id, Curriculum.school_id == school_id
            )
        )
        if not record:
            raise HTTPException(404, "Curriculum not found")
        return RetrievedContext(
            text=f"{record.title} ({record.subject}, {record.grade})\n{record.objectives[:12000]}",
            sources=[Source(id=record.id, title=record.title)],
        )
