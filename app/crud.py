from __future__ import annotations

from typing import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, schemas


async def create_exam(session: AsyncSession, data: schemas.ExamCreate) -> models.Exam:
    exam = models.Exam(
        title=data.title,
        description=data.description,
        created_by=data.created_by,
    )
    session.add(exam)
    await session.commit()
    await session.refresh(exam)
    return exam


async def get_exam(session: AsyncSession, exam_id: UUID) -> models.Exam | None:
    result = await session.execute(select(models.Exam).where(models.Exam.id == exam_id))
    return result.scalar_one_or_none()


async def create_questions(
    session: AsyncSession, exam_id: UUID, questions: Sequence[schemas.QuestionCreate]
) -> list[models.Question]:
    question_models: list[models.Question] = []
    for question in questions:
        question_model = models.Question(
            exam_id=exam_id,
            question_number=question.question_number,
            type=question.type,
            marks=question.marks,
            text=question.text,
        )
        session.add(question_model)
        question_models.append(question_model)
    await session.commit()
    for question_model in question_models:
        await session.refresh(question_model)
    return question_models


async def get_question(session: AsyncSession, question_id: UUID) -> models.Question | None:
    result = await session.execute(select(models.Question).where(models.Question.id == question_id))
    return result.scalar_one_or_none()


async def create_rubric(
    session: AsyncSession, question_id: UUID, data: schemas.RubricCreate
) -> models.Rubric:
    rubric = models.Rubric(
        question_id=question_id,
        key_points=data.key_points,
        marking_scheme=data.marking_scheme,
        strictness=data.strictness,
    )
    session.add(rubric)
    await session.commit()
    await session.refresh(rubric)
    return rubric
