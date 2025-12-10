from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.course import Course


class CourseService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, course_id: int) -> Course | None:
        return self.db.get(Course, course_id)

    def get_all(self, skip: int = 0, limit: int = 100) -> list[Course]:
        stmt = select(Course).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_teacher(self, teacher_id: int) -> list[Course]:
        stmt = select(Course).where(Course.teacher_id == teacher_id)
        return list(self.db.execute(stmt).scalars().all())

    def get_published(self, skip: int = 0, limit: int = 100) -> list[Course]:
        stmt = select(Course).where(Course.is_published == True).offset(skip).limit(limit)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, title: str, teacher_id: int, description: str = None, source_content: str = None) -> Course:
        course = Course(
            title=title,
            description=description,
            source_content=source_content,
            teacher_id=teacher_id,
        )
        self.db.add(course)
        self.db.commit()
        self.db.refresh(course)
        return course

    def update(self, course_id: int, **kwargs) -> Course | None:
        course = self.get_by_id(course_id)
        if not course:
            return None
        for key, value in kwargs.items():
            if hasattr(course, key) and value is not None:
                setattr(course, key, value)
        self.db.commit()
        self.db.refresh(course)
        return course

    def publish(self, course_id: int) -> Course | None:
        return self.update(course_id, is_published=True)

    def unpublish(self, course_id: int) -> Course | None:
        return self.update(course_id, is_published=False)

    def delete(self, course_id: int) -> bool:
        course = self.get_by_id(course_id)
        if not course:
            return False
        self.db.delete(course)
        self.db.commit()
        return True
