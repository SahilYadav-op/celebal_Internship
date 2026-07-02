"""Database operations for questions and choices."""
from typing import List, Optional

from sqlalchemy.orm import Session, selectinload

from app import models, schemas


# question crud

def create_question(db: Session, payload: schemas.QuestionCreate) -> models.Question:
    question = models.Question(**payload.model_dump())
    db.add(question)
    db.commit()
    db.refresh(question)
    return get_question(db, question.id)


def get_question(db: Session, question_id: int) -> Optional[models.Question]:
    return (
        db.query(models.Question)
        .options(selectinload(models.Question.choices))
        .filter(models.Question.id == question_id)
        .first()
    )


def get_questions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
) -> List[models.Question]:
    query = db.query(models.Question).options(selectinload(models.Question.choices))
    if category:
        query = query.filter(models.Question.category == category)
    return query.order_by(models.Question.id).offset(skip).limit(limit).all()


def update_question(
    db: Session,
    question: models.Question,
    payload: schemas.QuestionUpdate,
) -> models.Question:
    # exclude_unset so only the fields sent by the client get changed
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(question, field, value)
    db.commit()
    return get_question(db, question.id)


def delete_question(db: Session, question: models.Question) -> None:
    db.delete(question)  # choices get deleted by the cascade
    db.commit()


# choice crud

def create_choice(db: Session, payload: schemas.ChoiceCreate) -> models.Choice:
    choice = models.Choice(**payload.model_dump())
    db.add(choice)
    db.commit()
    db.refresh(choice)
    return choice


def get_choice(db: Session, choice_id: int) -> Optional[models.Choice]:
    return db.query(models.Choice).filter(models.Choice.id == choice_id).first()


def get_choices(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    question_id: Optional[int] = None,
) -> List[models.Choice]:
    query = db.query(models.Choice)
    if question_id is not None:
        query = query.filter(models.Choice.question_id == question_id)
    return query.order_by(models.Choice.id).offset(skip).limit(limit).all()


def update_choice(
    db: Session,
    choice: models.Choice,
    payload: schemas.ChoiceUpdate,
) -> models.Choice:
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(choice, field, value)
    db.commit()
    db.refresh(choice)
    return choice


def delete_choice(db: Session, choice: models.Choice) -> None:
    db.delete(choice)
    db.commit()
