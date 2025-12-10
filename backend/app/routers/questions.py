from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.question import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionWithOptions,
    OptionCreate,
    OptionUpdate,
    OptionResponse,
)
from app.services.question_service import QuestionService

router = APIRouter(prefix="/lessons/{lesson_id}/questions", tags=["questions"])


@router.get("/", response_model=list[QuestionResponse])
def get_questions(lesson_id: int, difficulty: str = None, db: Session = Depends(get_db)):
    service = QuestionService(db)
    if difficulty:
        return service.get_by_difficulty(lesson_id, difficulty)
    return service.get_by_lesson(lesson_id)


@router.get("/{question_id}", response_model=QuestionWithOptions)
def get_question(lesson_id: int, question_id: int, db: Session = Depends(get_db)):
    service = QuestionService(db)
    question = service.get_by_id(question_id)
    if not question or question.lesson_id != lesson_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    options = service.get_options(question_id)
    return QuestionWithOptions(
        id=question.id,
        text=question.text,
        question_type=question.question_type,
        difficulty=question.difficulty,
        lesson_id=question.lesson_id,
        created_at=question.created_at,
        updated_at=question.updated_at,
        options=[OptionResponse.model_validate(o) for o in options],
    )


@router.post("/", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(lesson_id: int, data: QuestionCreate, db: Session = Depends(get_db)):
    service = QuestionService(db)
    question = service.create(
        text=data.text,
        lesson_id=lesson_id,
        question_type=data.question_type,
        difficulty=data.difficulty,
    )
    if data.options:
        for opt in data.options:
            service.add_option(question.id, opt.text, opt.is_correct)
    return question


@router.patch("/{question_id}", response_model=QuestionResponse)
def update_question(lesson_id: int, question_id: int, data: QuestionUpdate, db: Session = Depends(get_db)):
    service = QuestionService(db)
    question = service.get_by_id(question_id)
    if not question or question.lesson_id != lesson_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return service.update(question_id, **data.model_dump(exclude_unset=True))


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(lesson_id: int, question_id: int, db: Session = Depends(get_db)):
    service = QuestionService(db)
    question = service.get_by_id(question_id)
    if not question or question.lesson_id != lesson_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    service.delete(question_id)


@router.post("/{question_id}/options", response_model=OptionResponse, status_code=status.HTTP_201_CREATED)
def add_option(lesson_id: int, question_id: int, data: OptionCreate, db: Session = Depends(get_db)):
    service = QuestionService(db)
    question = service.get_by_id(question_id)
    if not question or question.lesson_id != lesson_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found")
    return service.add_option(question_id, data.text, data.is_correct)


@router.patch("/{question_id}/options/{option_id}", response_model=OptionResponse)
def update_option(lesson_id: int, question_id: int, option_id: int, data: OptionUpdate, db: Session = Depends(get_db)):
    service = QuestionService(db)
    option = service.update_option(option_id, **data.model_dump(exclude_unset=True))
    if not option or option.question_id != question_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option not found")
    return option


@router.delete("/{question_id}/options/{option_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_option(lesson_id: int, question_id: int, option_id: int, db: Session = Depends(get_db)):
    service = QuestionService(db)
    if not service.delete_option(option_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Option not found")
