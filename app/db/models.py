from __future__ import annotations

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .base import Base


class TestGroup(Base):
    """测试组（中文注释）：使用流水号标识，一个组包含多张图片。"""
    __tablename__ = "test_groups"

    id = Column(Integer, primary_key=True, index=True)
    serial = Column(String(64), unique=True, nullable=False, index=True)
    note = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    images = relationship("TestImage", back_populates="group", cascade="all, delete-orphan")


class TestImage(Base):
    """测试图片（中文注释）：归属于某个测试组，记录相对路径。"""
    __tablename__ = "test_images"
    __table_args__ = (
        UniqueConstraint("group_id", "filename", name="uq_group_filename"),
    )

    id = Column(Integer, primary_key=True, index=True)
    group_id = Column(Integer, ForeignKey("test_groups.id", ondelete="CASCADE"), nullable=False)
    filename = Column(String(255), nullable=False)
    rel_path = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    group = relationship("TestGroup", back_populates="images")
