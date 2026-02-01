from typing import Optional, List
import enum
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, Text, JSON, DateTime, ForeignKey, func


# Базовый класс для всех моделей SQLAlchemy
class Base(DeclarativeBase):
    pass

# Перечисление ролей пользователей
class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"

# Перечисление статусов проектов
class ProjectStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    FEATURED = "FEATURED"

# Модель события ленты времени
class TimelineEventModel(Base):
    __tablename__ = "timeline_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

# Модель героев авиации и космонавтики
class HeroModel(Base):
    __tablename__ = "heroes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    era: Mapped[str] = mapped_column(String(50), nullable=False, default="XX век")
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    birth_date: Mapped[Optional[str]] = mapped_column(String(50))
    death_date: Mapped[Optional[str]] = mapped_column(String(50))
    achievements: Mapped[Optional[str]] = mapped_column(Text)
    biography: Mapped[Optional[str]] = mapped_column(Text)

# Модель пользователя
class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)

# Модель проекта КБ Будущего
class ProjectModel(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    user_name = Column(String(255), nullable=False)
    user_email = Column(String(255), nullable=False)
    user_phone = Column(String(50))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    project_type = Column(String(50), nullable=False)
    file_path = Column(String(500))
    file_name = Column(String(255))
    file_size = Column(Integer)

    # Используем строковый тип для статуса вместо Enum для упрощения
    status = Column(String(50), default="PENDING", nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    admin_comment = Column(Text)
    rating = Column(Integer, default=0)
    votes_count = Column(Integer, default=0)

