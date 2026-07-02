"""Pydantic schemas for request validation and responses."""
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


# choice schemas

class ChoiceBase(BaseModel):
    choice_text: str = Field(..., min_length=1, max_length=500)
    is_correct: bool = False


class ChoiceCreate(ChoiceBase):
    model_config = ConfigDict(extra="forbid")
    question_id: int


class ChoiceUpdate(BaseModel):
    # all optional so you can update only the fields you want
    model_config = ConfigDict(extra="forbid")
    choice_text: Optional[str] = Field(default=None, min_length=1, max_length=500)
    is_correct: Optional[bool] = None


class ChoiceResponse(ChoiceBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    question_id: int


# question schemas

class QuestionBase(BaseModel):
    question_text: str = Field(..., min_length=1, max_length=1000)
    category: Optional[str] = Field(default=None, max_length=100)


class QuestionCreate(QuestionBase):
    model_config = ConfigDict(extra="forbid")


class QuestionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question_text: Optional[str] = Field(default=None, min_length=1, max_length=1000)
    category: Optional[str] = Field(default=None, max_length=100)


class QuestionResponse(QuestionBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    choices: List[ChoiceResponse] = []
