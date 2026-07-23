import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

log = logging.getLogger(__name__)

# Primary PostgreSQL / configured DATABASE_URL
db_url = settings.DATABASE_URL

try:
    if "postgresql" in db_url:
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
        )
        # Test connection
        with engine.connect() as conn:
            pass
        log.info("Connected to primary PostgreSQL database.")
    else:
        engine = create_engine(
            db_url,
            connect_args={"check_same_thread": False} if "sqlite" in db_url else {},
        )
except Exception as e:
    log.warning("Primary database connection (%s) failed (%s). Falling back to local SQLite database.", db_url, e)
    sqlite_url = "sqlite:///./acadeval_fallback.db"
    engine = create_engine(
        sqlite_url,
        connect_args={"check_same_thread": False},
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
