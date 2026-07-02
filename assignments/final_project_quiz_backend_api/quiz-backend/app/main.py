"""Main FastAPI app. Run with: uvicorn app.main:app --reload"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401  (needed so create_all sees the models)
from app.config import settings
from app.database import Base, engine
from app.routers import choices, questions

# create tables on startup if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="A RESTful API to create and manage quiz questions and their answer choices.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(questions.router)
app.include_router(choices.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": f"Welcome to the {settings.APP_NAME}",
        "docs": "/docs",
        "health": "/health",
    }


@app.get("/health", tags=["Root"])
def health():
    return {"status": "ok"}
