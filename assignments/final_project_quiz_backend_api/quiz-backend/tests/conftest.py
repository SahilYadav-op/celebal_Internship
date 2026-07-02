import os

# use a separate db file for tests (must be set before importing the app)
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_quiz.db")

import pytest
from fastapi.testclient import TestClient

from app.database import Base, engine
from app.main import app


@pytest.fixture(autouse=True)
def setup_database():
    # fresh tables for every test
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
