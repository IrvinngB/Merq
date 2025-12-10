from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.module import Module


class ModuleService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, module_id: int) -> Module | None:
        return self.db.get(Module, module_id)

    def get_by_course(self, course_id: int) -> list[Module]:
        stmt = select(Module).where(Module.course_id == course_id).order_by(Module.position)
        return list(self.db.execute(stmt).scalars().all())

    def create(self, title: str, course_id: int, description: str = None) -> Module:
        next_position = self._get_next_position(course_id)
        module = Module(
            title=title,
            description=description,
            course_id=course_id,
            position=next_position,
        )
        self.db.add(module)
        self.db.commit()
        self.db.refresh(module)
        return module

    def update(self, module_id: int, **kwargs) -> Module | None:
        module = self.get_by_id(module_id)
        if not module:
            return None
        for key, value in kwargs.items():
            if hasattr(module, key) and value is not None:
                setattr(module, key, value)
        self.db.commit()
        self.db.refresh(module)
        return module

    def reorder(self, module_id: int, new_position: int) -> Module | None:
        return self.update(module_id, position=new_position)

    def delete(self, module_id: int) -> bool:
        module = self.get_by_id(module_id)
        if not module:
            return False
        self.db.delete(module)
        self.db.commit()
        return True

    def _get_next_position(self, course_id: int) -> int:
        stmt = select(func.coalesce(func.max(Module.position), -1) + 1).where(
            Module.course_id == course_id
        )
        return self.db.execute(stmt).scalar()
