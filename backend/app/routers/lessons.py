from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.lesson import LessonCreate, LessonUpdate, LessonResponse
from app.services.lesson_service import LessonService

router = APIRouter(prefix="/modules/{module_id}/lessons", tags=["lessons"])


@router.get("/", response_model=list[LessonResponse])
def get_lessons(module_id: int, db: Session = Depends(get_db)):
    service = LessonService(db)
    return service.get_by_module(module_id)


@router.get("/{lesson_id}", response_model=LessonResponse)
def get_lesson(module_id: int, lesson_id: int, db: Session = Depends(get_db)):
    service = LessonService(db)
    lesson = service.get_by_id(lesson_id)
    if not lesson or lesson.module_id != module_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return lesson


@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(module_id: int, data: LessonCreate, db: Session = Depends(get_db)):
    service = LessonService(db)
    return service.create(
        title=data.title,
        content=data.content,
        module_id=module_id,
    )


@router.patch("/{lesson_id}", response_model=LessonResponse)
def update_lesson(module_id: int, lesson_id: int, data: LessonUpdate, db: Session = Depends(get_db)):
    service = LessonService(db)
    lesson = service.get_by_id(lesson_id)
    if not lesson or lesson.module_id != module_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return service.update(lesson_id, **data.model_dump(exclude_unset=True))


@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(module_id: int, lesson_id: int, db: Session = Depends(get_db)):
    service = LessonService(db)
    lesson = service.get_by_id(lesson_id)
    if not lesson or lesson.module_id != module_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    service.delete(lesson_id)
