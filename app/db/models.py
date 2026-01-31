from typing import Optional, List
import enum
from datetime import datetime

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, Text, JSON, DateTime, ForeignKey


# Базовый класс для таблиц
class Base(DeclarativeBase):
    pass


# Класс для ролей пользователей
class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"


# Статусы проектов
class ProjectStatus(enum.Enum):
    PENDING = "pending"  # На рассмотрении
    APPROVED = "approved"  # Одобрено
    REJECTED = "rejected"  # Отклонено
    FEATURED = "featured"  # В зале славы


# Модель для событий ленты времени
class TimelineEventModel(Base):
    __tablename__ = "timeline_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)


# Модель для героев авиации и космонавтики
class HeroModel(Base):
    __tablename__ = "heroes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    # Основные данные для карточки
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    role: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    era: Mapped[str] = mapped_column(String(50), nullable=False, default="XX век")
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)

    # Для модального окна
    birth_date: Mapped[Optional[str]] = mapped_column(String(50))
    death_date: Mapped[Optional[str]] = mapped_column(String(50))
    achievements: Mapped[Optional[str]] = mapped_column(Text)
    biography: Mapped[Optional[str]] = mapped_column(Text)


# Таблица для хранения данных пользователя
class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)


# Модель для проектов КБ Будущего
class ProjectModel(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    user_name: Mapped[str] = mapped_column(String(100), nullable=False)
    user_email: Mapped[str] = mapped_column(String(255), nullable=False)
    user_phone: Mapped[str] = mapped_column(String(20), nullable=False)

    # Информация о проекте
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    project_type: Mapped[str] = mapped_column(String(50), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_name: Mapped[str] = mapped_column(String(200), nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, nullable=False) 

    # Статус и даты
    status: Mapped[str] = mapped_column(SQLEnum(ProjectStatus), default=ProjectStatus.PENDING)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    admin_comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Рейтинг и оценки
    rating: Mapped[int] = mapped_column(Integer, default=0)
    votes_count: Mapped[int] = mapped_column(Integer, default=0)

