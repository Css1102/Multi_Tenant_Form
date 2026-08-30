from sqlmodel import create_engine, Session
import os
import os

DATABASE_URL = os.getenv("DATABASE_URL", "").replace(
    "postgres://", "postgresql://", 1
)
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    """Dependency to provide a database session per request."""
    with Session(engine) as session:
        yield session