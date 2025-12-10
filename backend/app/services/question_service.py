from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.question import Question, QuestionOption, DifficultyLevel, QuestionType


class QuestionService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, question_id: int) -> Question | None:
        return self.db.get(Question, question_id)

    def get_by_lesson(self, lesson_id: int) -> list[Question]:
        stmt = select(Question).where(Question.lesson_id == lesson_id)
        return list(self.db.execute(stmt).scalars().all())

    def get_by_difficulty(self, lesson_id: int, difficulty: str) -> list[Question]:
        stmt = select(Question).where(
            Question.lesson_id == lesson_id,
            Question.difficulty == difficulty
        )
        return list(self.db.execute(stmt).scalars().all())

    def create(
        self,
        text: str,
        lesson_id: int,
        question_type: str = QuestionType.MULTIPLE_CHOICE,
        difficulty: str = DifficultyLevel.MEDIUM,
    ) -> Question:
        question = Question(
            text=text,
            lesson_id=lesson_id,
            question_type=question_type,
            difficulty=difficulty,
        )
        self.db.add(question)
        self.db.commit()
        self.db.refresh(question)
        return question

    def update(self, question_id: int, **kwargs) -> Question | None:
        question = self.get_by_id(question_id)
        if not question:
            return None
        for key, value in kwargs.items():
            if hasattr(question, key) and value is not None:
                setattr(question, key, value)
        self.db.commit()
        self.db.refresh(question)
        return question

    def delete(self, question_id: int) -> bool:
        question = self.get_by_id(question_id)
        if not question:
            return False
        self.db.delete(question)
        self.db.commit()
        return True

    def get_options(self, question_id: int) -> list[QuestionOption]:
        stmt = select(QuestionOption).where(QuestionOption.question_id == question_id)
        return list(self.db.execute(stmt).scalars().all())

    def add_option(self, question_id: int, text: str, is_correct: bool = False) -> QuestionOption:
        option = QuestionOption(
            text=text,
            is_correct=is_correct,
            question_id=question_id,
        )
        self.db.add(option)
        self.db.commit()
        self.db.refresh(option)
        return option

    def update_option(self, option_id: int, **kwargs) -> QuestionOption | None:
        option = self.db.get(QuestionOption, option_id)
        if not option:
            return None
        for key, value in kwargs.items():
            if hasattr(option, key) and value is not None:
                setattr(option, key, value)
        self.db.commit()
        self.db.refresh(option)
        return option

    def delete_option(self, option_id: int) -> bool:
        option = self.db.get(QuestionOption, option_id)
        if not option:
            return False
        self.db.delete(option)
        self.db.commit()
        return True
