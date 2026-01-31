from typing import Optional, List
import enum

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Column, Integer, String, Enum as SQLEnum, Text, JSON


class Base(DeclarativeBase):
    pass


class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"


class TimelineEventModel(Base):
    """Модель для событий ленты времени"""
    __tablename__ = "timeline_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # "1903"
    title: Mapped[str] = mapped_column(String(200), nullable=False)  # "Первый полёт братьев Райт"
    description: Mapped[str] = mapped_column(Text, nullable=False)  # Описание события


class HeroModel(Base):
    """Модель для героев авиации и космонавтики"""
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



class UserModel(Base):
    """Таблица для хранения данных пользователя"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(), nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)