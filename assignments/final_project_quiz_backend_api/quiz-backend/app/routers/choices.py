from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter(prefix="/choices", tags=["Choices"])


@router.post("", response_model=schemas.ChoiceResponse, status_code=status.HTTP_201_CREATED)
def create_choice(payload: schemas.ChoiceCreate, db: Session = Depends(get_db)):
    """Add a new answer choice to an existing question."""
    if crud.get_question(db, payload.question_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Question {payload.question_id} not found.",
        )
    return crud.create_choice(db, payload)


@router.get("", response_model=list[schemas.ChoiceResponse])
def list_choices(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    question_id: int | None = Query(None, description="Filter choices by question."),
    db: Session = Depends(get_db),
):
    """Retrieve all answer choices (optionally filtered by question)."""
    return crud.get_choices(db, skip=skip, limit=limit, question_id=question_id)


@router.get("/{choice_id}", response_model=schemas.ChoiceResponse)
def get_choice(choice_id: int, db: Session = Depends(get_db)):
    """Retrieve a specific answer choice."""
    choice = crud.get_choice(db, choice_id)
    if choice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Choice {choice_id} not found.")
    return choice


@router.put("/{choice_id}", response_model=schemas.ChoiceResponse)
def update_choice(choice_id: int, payload: schemas.ChoiceUpdate, db: Session = Depends(get_db)):
    """Update an answer choice."""
    choice = crud.get_choice(db, choice_id)
    if choice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Choice {choice_id} not found.")
    return crud.update_choice(db, choice, payload)


@router.delete("/{choice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_choice(choice_id: int, db: Session = Depends(get_db)):
    """Delete an answer choice."""
    choice = crud.get_choice(db, choice_id)
    if choice is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Choice {choice_id} not found.")
    crud.delete_choice(db, choice)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
