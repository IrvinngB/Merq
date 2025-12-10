from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.sql import func

from app.core.database import Base


class Attempt(Base):
    """Tabla de hechos central (topología estrella)."""
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False, index=True)
    selected_option_id = Column(Integer, ForeignKey("question_options.id", ondelete="SET NULL"), nullable=True)
    answer_text = Column(Text, nullable=True)
    is_correct = Column(Boolean, default=False)
    response_time_seconds = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
