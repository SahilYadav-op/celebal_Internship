# Quiz Backend Management API using FastAPI

A RESTful backend for creating and managing quiz questions and answer choices, with full CRUD operations and a relational database. Built with FastAPI, SQLAlchemy ORM and Pydantic. It also includes a Streamlit dashboard that consumes the API, so the backend can be tested and demoed visually.

**Final Project - Celebal Technologies Internship**
**Author**: Sahil Yadav

## Overview

The project is a general purpose quiz management system (Option 1 from the project document). Every question can have a category like General Knowledge, Programming, Mathematics, Data Science, Business Studies or Aptitude, so quizzes from multiple domains can live in the same database.

There are two parts:

1. **quiz-backend/** - the FastAPI REST API (the main project)
2. **dashboard/** - a Streamlit app that calls the API, with analytics charts, CRUD forms and a "take a quiz" mode

## System Architecture

```
Client Request
      |
      v
FastAPI Routes        (app/routers/questions.py, choices.py)
      |
      v
Business Logic        (app/crud.py)
      |
      v
SQLAlchemy ORM        (app/models.py)
      |
      v
Database              (SQLite by default, PostgreSQL/MySQL supported)
```

Validation of request/response data is handled by Pydantic schemas (app/schemas.py).

## Database Design

**Question Table**

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary Key |
| question_text | String | Stores the quiz question |
| category | String | Quiz category/domain (optional) |

**Choice Table**

| Field | Type | Description |
|-------|------|-------------|
| id | Integer | Primary Key |
| choice_text | String | Answer option |
| is_correct | Boolean | Indicates the correct answer |
| question_id | Integer | Foreign Key referencing Question |

**Relationship**: One Question has many Choices. Deleting a question also deletes its choices (cascade).

## API Endpoints

### Question Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /questions | Create a new quiz question |
| GET | /questions | Get all questions (supports ?category= filter) |
| GET | /questions/{id} | Get a specific question with its choices |
| PUT | /questions/{id} | Update an existing question |
| DELETE | /questions/{id} | Delete a question and its choices |

### Choice Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /choices | Add a new answer choice |
| GET | /choices | Get all answer choices (supports ?question_id= filter) |
| GET | /choices/{id} | Get a specific choice |
| PUT | /choices/{id} | Update an answer choice |
| DELETE | /choices/{id} | Delete an answer choice |

## Project Structure

```
├── quiz-backend/
│   ├── app/
│   │   ├── config.py          # settings loaded from .env
│   │   ├── database.py        # engine, session, get_db dependency
│   │   ├── models.py          # Question and Choice ORM models
│   │   ├── schemas.py         # Pydantic request/response schemas
│   │   ├── crud.py            # database operations
│   │   ├── main.py            # FastAPI app entry point
│   │   └── routers/
│   │       ├── questions.py   # /questions endpoints
│   │       └── choices.py     # /choices endpoints
│   ├── tests/                 # pytest API tests
│   ├── seed.py                # loads sample questions
│   ├── requirements.txt
│   └── .env.example
└── dashboard/
    ├── streamlit_app.py       # dashboard entry point
    ├── api_client.py          # functions that call the API with requests
    └── views/
        ├── analytics.py       # charts and stats
        ├── manage.py          # CRUD forms
        └── quiz.py            # interactive quiz with scoring
```

## Setup & Usage

### 1. Create virtual environment
```bash
cd quiz-backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. (Optional) Load sample questions
```bash
python seed.py
```

### 4. Run the API
```bash
uvicorn app.main:app --reload
```

Then open:
- Swagger docs: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

### 5. Run the dashboard (optional, in a second terminal)
Open a new terminal in the project root (not inside quiz-backend/):
```bash
pip install -r dashboard/requirements.txt
streamlit run dashboard/streamlit_app.py
```

The dashboard connects to the API at http://127.0.0.1:8000 by default (can be changed from the sidebar).

## Example Requests

```bash
# create a question
curl -X POST http://127.0.0.1:8000/questions -H "Content-Type: application/json" -d "{\"question_text\": \"What is the capital of France?\", \"category\": \"General Knowledge\"}"

# add a choice to question 1
curl -X POST http://127.0.0.1:8000/choices -H "Content-Type: application/json" -d "{\"choice_text\": \"Paris\", \"is_correct\": true, \"question_id\": 1}"

# get the question with its choices
curl http://127.0.0.1:8000/questions/1
```

## Testing

```bash
cd quiz-backend
pytest
```

11 tests cover question and choice CRUD, category filtering, cascade delete, 404 handling and request validation. Tests run on a separate test database.

## Switching Databases

The database is selected by the `DATABASE_URL` value in `.env` (see `.env.example`):

```
# SQLite (default, no setup needed)
DATABASE_URL=sqlite:///./quiz.db

# PostgreSQL
DATABASE_URL=postgresql+psycopg://user:password@localhost:5432/quiz
```

No code changes are needed to switch.

## Key Learnings

- Building REST APIs with FastAPI (routers, dependencies, status codes)
- Database design and one-to-many relationships with SQLAlchemy ORM
- Request/response validation using Pydantic models
- Managing database sessions per request with dependency injection
- Writing API tests with pytest and FastAPI's TestClient
- Consuming a REST API from a frontend (Streamlit + requests)

## Future Enhancements

- User authentication and authorization
- Timer based quizzes
- Score and leaderboard management
- Quiz attempt history
- Bulk import of questions from CSV/JSON

## Conclusion

This project covers the complete backend development cycle: designing a relational schema, exposing it through a validated REST API, testing it, and integrating it with a client application. The same API could be consumed by a web or mobile app in place of the Streamlit dashboard.
