from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMBaseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UserBase(ORMBaseModel):
    name: str
    email: str
    role: str


class UserCreate(UserBase):
    pass


class UserRead(UserBase):
    id: UUID
    created_at: datetime


class ExamBase(ORMBaseModel):
    title: str
    description: Optional[str] = None


class ExamCreate(ExamBase):
    created_by: UUID


class ExamRead(ExamBase):
    id: UUID
    created_at: datetime
    created_by: UUID


class QuestionBase(ORMBaseModel):
    question_number: int
    type: str
    marks: int
    text: str


class QuestionCreate(QuestionBase):
    pass


class QuestionRead(QuestionBase):
    id: UUID
    exam_id: UUID


class RubricBase(ORMBaseModel):
    key_points: Dict[str, Any]
    marking_scheme: Dict[str, Any]
    strictness: str


class RubricCreate(RubricBase):
    pass


class RubricRead(RubricBase):
    id: UUID
    question_id: UUID


class SubmissionBase(ORMBaseModel):
    exam_id: UUID
    student_id: UUID


class SubmissionCreate(SubmissionBase):
    pass


class SubmissionRead(SubmissionBase):
    id: UUID
    uploaded_at: datetime
    total_marks: Optional[float] = None
    exam: Optional[ExamRead] = None


class AnswerBase(ORMBaseModel):
    submission_id: UUID
    question_id: UUID
    content: str
    marks_awarded: Optional[float] = None
    evaluation_data: Optional[Dict[str, Any]] = None


class AnswerCreate(AnswerBase):
    pass


class AnswerRead(AnswerBase):
    id: UUID
    submission: Optional[SubmissionRead] = None
    question: Optional[QuestionRead] = None
