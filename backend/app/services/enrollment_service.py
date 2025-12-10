from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.enrollment import Enrollment, EnrollmentStatus


class EnrollmentService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, enrollment_id: int) -> Enrollment | None:
        return self.db.get(Enrollment, enrollment_id)

    def get_by_student(self, student_id: int) -> list[Enrollment]:
        stmt = select(Enrollment).where(Enrollment.student_id == student_id)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_course(self, course_id: int) -> list[Enrollment]:
        stmt = select(Enrollment).where(Enrollment.course_id == course_id)
        return list(self.db.execute(stmt).scalars().all())

    def get_active_by_student(self, student_id: int) -> list[Enrollment]:
        stmt = select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.status == EnrollmentStatus.ACTIVE
        )
        return list(self.db.execute(stmt).scalars().all())

    def is_enrolled(self, student_id: int, course_id: int) -> bool:
        stmt = select(Enrollment).where(
            Enrollment.student_id == student_id,
            Enrollment.course_id == course_id,
            Enrollment.status == EnrollmentStatus.ACTIVE
        )
        return self.db.execute(stmt).scalar_one_or_none() is not None

    def enroll(self, student_id: int, course_id: int) -> Enrollment:
        existing = self.db.execute(
            select(Enrollment).where(
                Enrollment.student_id == student_id,
                Enrollment.course_id == course_id
            )
        ).scalar_one_or_none()

        if existing:
            existing.status = EnrollmentStatus.ACTIVE
            self.db.commit()
            self.db.refresh(existing)
            return existing

        enrollment = Enrollment(
            student_id=student_id,
            course_id=course_id,
        )
        self.db.add(enrollment)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def update_progress(self, enrollment_id: int, progress: int) -> Enrollment | None:
        enrollment = self.get_by_id(enrollment_id)
        if not enrollment:
            return None
        enrollment.progress_percentage = min(100, max(0, progress))
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def complete(self, enrollment_id: int) -> Enrollment | None:
        enrollment = self.get_by_id(enrollment_id)
        if not enrollment:
            return None
        enrollment.status = EnrollmentStatus.COMPLETED
        enrollment.progress_percentage = 100
        from datetime import datetime, timezone
        enrollment.completed_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment

    def drop(self, enrollment_id: int) -> Enrollment | None:
        enrollment = self.get_by_id(enrollment_id)
        if not enrollment:
            return None
        enrollment.status = EnrollmentStatus.DROPPED
        self.db.commit()
        self.db.refresh(enrollment)
        return enrollment
