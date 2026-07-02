from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

# sqlite needs check_same_thread=False because FastAPI may handle
# requests on different threads
is_sqlite = settings.DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if is_sqlite else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)


# sqlite does not enforce foreign keys by default, this turns it on
# so that ON DELETE CASCADE actually works
if is_sqlite:

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)

Base = declarative_base()


# dependency for routes, gives each request its own db session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
