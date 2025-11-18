from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum as PyEnum
from typing import List, Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Base(DeclarativeBase):
    pass


class UserRole(str, PyEnum):
    TEACHER = "teacher"
    STUDENT = "student"
    ADMIN = "admin"


class QuestionType(str, PyEnum):
    MCQ = "mcq"
    BLANK = "blank"
    SHORT = "short"
    LONG = "long"
    DIAGRAM = "diagram"
    MATH = "math"
    CODE = "code"


class RubricStrictness(str, PyEnum):
    TOUGH = "tough"
    NEUTRAL = "neutral"
    LENIENT = "lenient"


class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole, name="user_role"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    student_profile: Mapped[Optional["Student"]] = relationship("Student", back_populates="user", uselist=False)
    exams_created: Mapped[List["Exam"]] = relationship("Exam", back_populates="creator")


class Student(Base):
    __tablename__ = "students"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    roll_number: Mapped[str] = mapped_column(String(100), nullable=False)
    class_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    user: Mapped[User] = relationship("User", back_populates="student_profile")
    submissions: Mapped[List["Submission"]] = relationship("Submission", back_populates="student")


class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_by: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    creator: Mapped[User] = relationship("User", back_populates="exams_created")
    questions: Mapped[List["Question"]] = relationship("Question", back_populates="exam")
    submissions: Mapped[List["Submission"]] = relationship("Submission", back_populates="exam")


class Question(Base):
    __tablename__ = "questions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    exam_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False)
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[QuestionType] = mapped_column(Enum(QuestionType, name="question_type"), nullable=False)
    marks: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)

    exam: Mapped[Exam] = relationship("Exam", back_populates="questions")
    rubric: Mapped[Optional["Rubric"]] = relationship("Rubric", back_populates="question", uselist=False)
    answers: Mapped[List["Answer"]] = relationship("Answer", back_populates="question")


class Rubric(Base):
    __tablename__ = "rubrics"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    question_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False, unique=True)
    key_points: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    marking_scheme: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    strictness: Mapped[RubricStrictness] = mapped_column(Enum(RubricStrictness, name="rubric_strictness"), nullable=False)

    question: Mapped[Question] = relationship("Question", back_populates="rubric")


class Submission(Base):
    __tablename__ = "submissions"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    exam_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("exams.id"), nullable=False)
    student_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("students.id"), nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    total_marks: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    exam: Mapped[Exam] = relationship("Exam", back_populates="submissions")
    student: Mapped[Student] = relationship("Student", back_populates="submissions")
    answers: Mapped[List["Answer"]] = relationship("Answer", back_populates="submission")


class Answer(Base):
    __tablename__ = "answers"

    id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid4)
    submission_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("submissions.id"), nullable=False)
    question_id: Mapped[UUID] = mapped_column(PG_UUID(as_uuid=True), ForeignKey("questions.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    marks_awarded: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    evaluation_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    submission: Mapped[Submission] = relationship("Submission", back_populates="answers")
    question: Mapped[Question] = relationship("Question", back_populates="answers")
