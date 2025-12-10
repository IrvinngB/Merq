from sqlalchemy.orm import Session
from sqlalchemy import select, func

from app.models.attempt import Attempt
from app.models.question import QuestionOption


class AttemptService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, attempt_id: int) -> Attempt | None:
        return self.db.get(Attempt, attempt_id)

    def get_by_student(self, student_id: int, limit: int = 100) -> list[Attempt]:
        stmt = (
            select(Attempt)
            .where(Attempt.student_id == student_id)
            .order_by(Attempt.created_at.desc())
            .limit(limit)
        )
        return list(self.db.execute(stmt).scalars().all())

    def get_by_question(self, question_id: int) -> list[Attempt]:
        stmt = select(Attempt).where(Attempt.question_id == question_id)
        return list(self.db.execute(stmt).scalars().all())

    def get_student_question_attempts(self, student_id: int, question_id: int) -> list[Attempt]:
        stmt = (
            select(Attempt)
            .where(Attempt.student_id == student_id, Attempt.question_id == question_id)
            .order_by(Attempt.created_at.desc())
        )
        return list(self.db.execute(stmt).scalars().all())

    def create(
        self,
        student_id: int,
        question_id: int,
        selected_option_id: int = None,
        answer_text: str = None,
        response_time_seconds: float = None,
    ) -> Attempt:
        is_correct = False
        if selected_option_id:
            option = self.db.get(QuestionOption, selected_option_id)
            is_correct = option.is_correct if option else False

        attempt = Attempt(
            student_id=student_id,
            question_id=question_id,
            selected_option_id=selected_option_id,
            answer_text=answer_text,
            is_correct=is_correct,
            response_time_seconds=response_time_seconds,
        )
        self.db.add(attempt)
        self.db.commit()
        self.db.refresh(attempt)
        return attempt

    def get_student_stats(self, student_id: int) -> dict:
        total_stmt = select(func.count(Attempt.id)).where(Attempt.student_id == student_id)
        correct_stmt = select(func.count(Attempt.id)).where(
            Attempt.student_id == student_id,
            Attempt.is_correct == True
        )
        avg_time_stmt = select(func.avg(Attempt.response_time_seconds)).where(
            Attempt.student_id == student_id,
            Attempt.response_time_seconds.isnot(None)
        )

        total = self.db.execute(total_stmt).scalar() or 0
        correct = self.db.execute(correct_stmt).scalar() or 0
        avg_time = self.db.execute(avg_time_stmt).scalar()

        return {
            "total_attempts": total,
            "correct_attempts": correct,
            "accuracy_rate": (correct / total * 100) if total > 0 else 0,
            "average_response_time": round(avg_time, 2) if avg_time else None,
        }

    def get_question_stats(self, question_id: int) -> dict:
        total_stmt = select(func.count(Attempt.id)).where(Attempt.question_id == question_id)
        correct_stmt = select(func.count(Attempt.id)).where(
            Attempt.question_id == question_id,
            Attempt.is_correct == True
        )

        total = self.db.execute(total_stmt).scalar() or 0
        correct = self.db.execute(correct_stmt).scalar() or 0

        return {
            "total_attempts": total,
            "correct_attempts": correct,
            "success_rate": (correct / total * 100) if total > 0 else 0,
        }
