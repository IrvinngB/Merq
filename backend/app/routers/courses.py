from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.course import CourseCreate, CourseUpdate, CourseResponse
from app.services.course_service import CourseService

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=list[CourseResponse])
def get_courses(skip: int = 0, limit: int = 100, published_only: bool = False, db: Session = Depends(get_db)):
    service = CourseService(db)
    if published_only:
        return service.get_published(skip=skip, limit=limit)
    return service.get_all(skip=skip, limit=limit)


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(course_id: int, db: Session = Depends(get_db)):
    service = CourseService(db)
    course = service.get_by_id(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.post("/", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(data: CourseCreate, teacher_id: int, db: Session = Depends(get_db)):
    service = CourseService(db)
    return service.create(
        title=data.title,
        description=data.description,
        teacher_id=teacher_id,
    )


@router.patch("/{course_id}", response_model=CourseResponse)
def update_course(course_id: int, data: CourseUpdate, db: Session = Depends(get_db)):
    service = CourseService(db)
    course = service.update(course_id, **data.model_dump(exclude_unset=True))
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.post("/{course_id}/publish", response_model=CourseResponse)
def publish_course(course_id: int, db: Session = Depends(get_db)):
    service = CourseService(db)
    course = service.publish(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.post("/{course_id}/unpublish", response_model=CourseResponse)
def unpublish_course(course_id: int, db: Session = Depends(get_db)):
    service = CourseService(db)
    course = service.unpublish(course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    service = CourseService(db)
    if not service.delete(course_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
