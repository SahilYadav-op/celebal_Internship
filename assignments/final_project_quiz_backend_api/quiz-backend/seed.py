"""Loads some sample quiz questions into the database.
Run: python seed.py (skips if questions already exist)
"""
from app import models
from app.database import Base, SessionLocal, engine

SAMPLE_QUESTIONS = [
    {
        "question_text": "What is the capital of France?",
        "category": "General Knowledge",
        "choices": [("Paris", True), ("London", False), ("Berlin", False), ("Madrid", False)],
    },
    {
        "question_text": "Which keyword is used to define a function in Python?",
        "category": "Programming",
        "choices": [("def", True), ("func", False), ("function", False), ("lambda", False)],
    },
    {
        "question_text": "What is 7 x 8?",
        "category": "Mathematics",
        "choices": [("54", False), ("56", True), ("64", False), ("48", False)],
    },
    {
        "question_text": "Which Python library is most commonly used for data manipulation?",
        "category": "Data Science",
        "choices": [("pandas", True), ("requests", False), ("flask", False), ("pillow", False)],
    },
    {
        "question_text": "In business, what does 'ROI' stand for?",
        "category": "Business Studies",
        "choices": [
            ("Return on Investment", True),
            ("Rate of Interest", False),
            ("Record of Income", False),
            ("Ratio of Inventory", False),
        ],
    },
    {
        "question_text": "A train covers 60 km in 40 minutes. What is its speed in km/h?",
        "category": "Aptitude",
        "choices": [("80", False), ("90", True), ("100", False), ("120", False)],
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.Question).count() > 0:
            print("Database already has questions, skipping seed.")
            return
        for item in SAMPLE_QUESTIONS:
            question = models.Question(
                question_text=item["question_text"],
                category=item["category"],
            )
            for text, is_correct in item["choices"]:
                question.choices.append(models.Choice(choice_text=text, is_correct=is_correct))
            db.add(question)
        db.commit()
        print(f"Added {len(SAMPLE_QUESTIONS)} sample questions.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
