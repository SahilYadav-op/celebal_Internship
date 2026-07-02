from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.database import Base


class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    question_text = Column(Text, nullable=False)
    category = Column(String(100), nullable=True, index=True)

    # one question has many choices, deleting a question deletes its choices too
    choices = relationship(
        "Choice",
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="Choice.id",
    )


class Choice(Base):
    __tablename__ = "choices"

    id = Column(Integer, primary_key=True, index=True)
    choice_text = Column(Text, nullable=False)
    is_correct = Column(Boolean, nullable=False, default=False)
    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    question = relationship("Question", back_populates="choices")
