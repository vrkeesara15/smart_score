from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, schemas
from app.database import get_session, init_db

app = FastAPI(title="Smart Score Backend")
router = APIRouter(prefix="/api")


@router.post("/exams", response_model=schemas.ExamRead)
async def create_exam(
    exam_in: schemas.ExamCreate, session: AsyncSession = Depends(get_session)
):
    exam = await crud.create_exam(session, exam_in)
    return exam


@router.post("/exams/{exam_id}/questions", response_model=list[schemas.QuestionRead])
async def create_exam_questions(
    exam_id: UUID,
    questions_in: list[schemas.QuestionCreate],
    session: AsyncSession = Depends(get_session),
):
    exam = await crud.get_exam(session, exam_id)
    if exam is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exam not found")

    questions = await crud.create_questions(session, exam_id, questions_in)
    return questions


@router.post("/questions/{question_id}/rubric", response_model=schemas.RubricRead)
async def create_question_rubric(
    question_id: UUID,
    rubric_in: schemas.RubricCreate,
    session: AsyncSession = Depends(get_session),
):
    question = await crud.get_question(session, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")

    rubric = await crud.create_rubric(session, question_id, rubric_in)
    return rubric


app.include_router(router)


@app.on_event("startup")
async def startup_event() -> None:
    await init_db()


@app.get("/health")
async def health_check():
    return {"status": "ok"}
