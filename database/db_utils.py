from database.db_session import SessionLocal
from contextlib import contextmanager

@contextmanager
def session_scope():
    """Fournit une session SQLAlchemy qui se ferme automatiquement."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()