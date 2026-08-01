from sqlmodel import create_engine, Session
import os
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:mysecretpassword@localhost:5434/form_engine_db"
)
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    """Dependency to provide a database session per request."""
    with Session(engine) as session:
        yield session