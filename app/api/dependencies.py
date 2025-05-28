from app.db.base import SessionLocal

def get_db():
    """
    Dependency that provides a database session for each request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
