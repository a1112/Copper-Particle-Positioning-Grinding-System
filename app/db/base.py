from __future__ import annotations

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


def _db_path() -> Path:
    """返回 SQLite 数据库文件路径（中文注释）。若无目录则创建。"""
    root = Path(__file__).resolve().parents[2]
    db_dir = root / "database"
    db_dir.mkdir(parents=True, exist_ok=True)
    return db_dir / "test.db"


DATABASE_URL = f"sqlite:///{_db_path()}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()


def get_engine():
    """获取 SQLAlchemy Engine（中文注释）。"""
    return engine


def init_db() -> None:
    """初始化数据库（中文注释）：导入模型并创建表。"""
    from . import models  # noqa: F401 确保模型导入
    Base.metadata.create_all(bind=engine)
