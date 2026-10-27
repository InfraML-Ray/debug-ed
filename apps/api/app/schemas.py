from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class CurriculumCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=200)
    subject: str = Field(min_length=1, max_length=100)
    grade: str = Field(min_length=1, max_length=50)
    objectives: str = Field(min_length=1, max_length=12000)


class CurriculumRead(CurriculumCreate, ORMModel):
    id: str


class LessonCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    title: str = Field(min_length=1, max_length=200)
    content: str = Field(min_length=1, max_length=20000)
    duration_minutes: int = Field(default=40, ge=5, le=480)
    curriculum_id: str | None = None


class LessonRead(LessonCreate, ORMModel):
    id: str


class MembershipRead(BaseModel):
    school_id: str
    school_name: str
    role: str


class MeRead(BaseModel):
    name: str
    schools: list[MembershipRead]
    auth_mode: Literal["demo", "cognito"]
    ai_provider: Literal["demo", "openrouter"]


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    message: str = Field(min_length=1, max_length=6000)
    conversation_id: str | None = None
    curriculum_id: str | None = None


class Source(BaseModel):
    id: str
    title: str


class ChatResponse(BaseModel):
    conversation_id: str
    answer: str
    provider: Literal["demo", "openrouter"]
    sources: list[Source]
