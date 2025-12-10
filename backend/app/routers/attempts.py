from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.attempt import AttemptCreate, AttemptResponse, StudentStats, QuestionStats
from app.services.attempt_service import AttemptService

router = APIRouter(prefix="/attempts", tags=["attempts"])


@router.get("/student/{student_id}", response_model=list[AttemptResponse])
def get_student_attempts(student_id: int, limit: int = 100, db: Session = Depends(get_db)):
    service = AttemptService(db)
    return service.get_by_student(student_id, limit=limit)


@router.get("/student/{student_id}/stats", response_model=StudentStats)
def get_student_stats(student_id: int, db: Session = Depends(get_db)):
    service = AttemptService(db)
    return service.get_student_stats(student_id)


@router.get("/question/{question_id}/stats", response_model=QuestionStats)
def get_question_stats(question_id: int, db: Session = Depends(get_db)):
    service = AttemptService(db)
    return service.get_question_stats(question_id)


@router.post("/", response_model=AttemptResponse, status_code=status.HTTP_201_CREATED)
def create_attempt(student_id: int, data: AttemptCreate, db: Session = Depends(get_db)):
    service = AttemptService(db)
    return service.create(
        student_id=student_id,
        question_id=data.question_id,
        selected_option_id=data.selected_option_id,
        answer_text=data.answer_text,
        response_time_seconds=data.response_time_seconds,
    )
