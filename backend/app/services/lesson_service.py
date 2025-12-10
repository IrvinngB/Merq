from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.lesson import Lesson


class LessonService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, lesson_id: int) -> Lesson | None:
        return self.db.get(Lesson, lesson_id)

    def get_by_module(self, module_id: int) -> list[Lesson]:
        stmt = select(Lesson).where(Lesson.module_id == module_id).order_by(Lesson.position)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, title: str, module_id: int, content: str = None) -> Lesson:
        next_position = self._get_next_position(module_id)
        lesson = Lesson(
            title=title,
            content=content,
            module_id=module_id,
            position=next_position,
        )
        self.db.add(lesson)
        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def update(self, lesson_id: int, **kwargs) -> Lesson | None:
        lesson = self.get_by_id(lesson_id)
        if not lesson:
            return None
        for key, value in kwargs.items():
            if hasattr(lesson, key) and value is not None:
                setattr(lesson, key, value)
        self.db.commit()
        self.db.refresh(lesson)
        return lesson

    def reorder(self, lesson_id: int, new_position: int) -> Lesson | None:
        return self.update(lesson_id, position=new_position)

    def delete(self, lesson_id: int) -> bool:
        lesson = self.get_by_id(lesson_id)
        if not lesson:
            return False
        self.db.delete(lesson)
        self.db.commit()
        return True

    def _get_next_position(self, module_id: int) -> int:
        stmt = select(func.coalesce(func.max(Lesson.position), -1) + 1).where(
            Lesson.module_id == module_id
        )
        return self.db.execute(stmt).scalar()
