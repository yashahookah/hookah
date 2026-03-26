import os
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

BASE_DIR = Path(__file__).resolve().parent
# Для облака: DB_PATH из env (например /data/expo_pos.db на Render)
DB_PATH = Path(os.environ.get("DB_PATH", str(BASE_DIR / "expo_pos.db")))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    # Важно для облака/мультипроцессинга: ждём блокировку SQLite вместо вечного подвиса.
    DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
)

# Улучшаем конкурентный доступ (особенно на хостинге) и избегаем "вечного" ожидания локов.
@event.listens_for(engine, "connect")
def _set_sqlite_pragmas(dbapi_connection, _connection_record):
    try:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.execute("PRAGMA busy_timeout=30000;")
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()
    except Exception:
        # Если вдруг не SQLite или драйвер не поддерживает — тихо пропускаем.
        pass

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

