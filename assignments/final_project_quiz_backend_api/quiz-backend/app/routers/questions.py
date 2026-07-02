from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/questions", tags=["Questions"])


@router.post("", response_model=schemas.QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_question(payload: schemas.QuestionCreate, db: Session = Depends(get_db)):
    """Create a new quiz question."""
    return crud.create_question(db, payload)


@router.get("", response_model=list[schemas.QuestionResponse])
def list_questions(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    category: str | None = Query(None, description="Filter questions by category."),
    db: Session = Depends(get_db),
):
    """Retrieve all questions (optionally filtered by category)."""
    return crud.get_questions(db, skip=skip, limit=limit, category=category)


@router.get("/{question_id}", response_model=schemas.QuestionResponse)
def get_question(question_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific question and its choices."""
    question = crud.get_question(db, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Question {question_id} not found.")
    return question


@router.put("/{question_id}", response_model=schemas.QuestionResponse)
def update_question(question_id: int, payload: schemas.QuestionUpdate, db: Session = Depends(get_db)):
    """Update an existing question."""
    question = crud.get_question(db, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Question {question_id} not found.")
    return crud.update_question(db, question, payload)


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_question(question_id: int, db: Session = Depends(get_db)):
    """Delete a question and all of its associated choices."""
    question = crud.get_question(db, question_id)
    if question is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Question {question_id} not found.")
    crud.delete_question(db, question)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
