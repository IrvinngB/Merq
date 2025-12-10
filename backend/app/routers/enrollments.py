from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse, ProgressUpdate
from app.services.enrollment_service import EnrollmentService

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


@router.get("/student/{student_id}", response_model=list[EnrollmentResponse])
def get_student_enrollments(student_id: int, db: Session = Depends(get_db)):
    service = EnrollmentService(db)
    return service.get_by_student(student_id)


@router.get("/course/{course_id}", response_model=list[EnrollmentResponse])
def get_course_enrollments(course_id: int, db: Session = Depends(get_db)):
    service = EnrollmentService(db)
    return service.get_by_course(course_id)


@router.post("/", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
def enroll_student(student_id: int, data: EnrollmentCreate, db: Session = Depends(get_db)):
    service = EnrollmentService(db)
    return service.enroll(student_id=student_id, course_id=data.course_id)


@router.patch("/{enrollment_id}/progress", response_model=EnrollmentResponse)
def update_progress(enrollment_id: int, data: ProgressUpdate, db: Session = Depends(get_db)):
    service = EnrollmentService(db)
    enrollment = service.update_progress(enrollment_id, data.progress_percentage)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    return enrollment


@router.post("/{enrollment_id}/complete", response_model=EnrollmentResponse)
def complete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    service = EnrollmentService(db)
    enrollment = service.complete(enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    return enrollment


@router.post("/{enrollment_id}/drop", response_model=EnrollmentResponse)
def drop_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    service = EnrollmentService(db)
    enrollment = service.drop(enrollment_id)
    if not enrollment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Enrollment not found")
    return enrollment
