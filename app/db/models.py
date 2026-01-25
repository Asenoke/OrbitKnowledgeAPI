from typing import Optional

from sqlalchemy import String, Boolean, Text, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimelineEventModel(Base):
    """Модель для событий ленты времени"""
    __tablename__ = "timeline_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    year: Mapped[str] = mapped_column(String(10), nullable=False, index=True)  # "1903"
    title: Mapped[str] = mapped_column(String(200), nullable=False)  # "Первый полёт братьев Райт"
    description: Mapped[str] = mapped_column(Text, nullable=False)  # Описание события
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # Флаг активности


class HeroModel(Base):
    """Модель для героев авиации и космонавтики"""
    __tablename__ = "heroes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)  # "Юрий Гагарин"
    role: Mapped[str] = mapped_column(String(100), nullable=False)  # "Первый человек в космосе"
    description: Mapped[str] = mapped_column(Text, nullable=False)  # Краткое описание
    image_url: Mapped[Optional[str]] = mapped_column(String(500))  # URL изображения
    era: Mapped[Optional[str]] = mapped_column(String(50))  # "XX век"
    tags: Mapped[Optional[str]] = mapped_column(String(200))  # "космонавт, СССР, рекорд"

    # Дополнительные данные для модального окна
    birth_date: Mapped[Optional[str]] = mapped_column(String(50))  # "9 марта 1934"
    death_date: Mapped[Optional[str]] = mapped_column(String(50))  # "27 марта 1968"
    achievements: Mapped[Optional[str]] = mapped_column(Text)  # Основные достижения
    biography: Mapped[Optional[str]] = mapped_column(Text)  # Полная биография
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)  # Флаг активности


class UserModel(Base):  # Изменено имя с user на UserModel
    """Таблица для хранения данных пользователя"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False, index=True)