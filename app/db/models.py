from sqlalchemy import Column, String, Boolean, Text, Integer
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class TimelineEvent(Base):
    """Модель для событий ленты времени"""
    __tablename__ = "timeline_events"

    id = Column(Integer, primary_key=True)
    year = Column(String(10), nullable=False, index=True)  # "1903"
    title = Column(String(200), nullable=False)  # "Первый полёт братьев Райт"
    description = Column(Text, nullable=False)  # Описание события
    is_active = Column(Boolean, default=True)  # Флаг активности


class Hero(Base):
    """Модель для героев авиации и космонавтики"""
    __tablename__ = "heroes"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)  # "Юрий Гагарин"
    role = Column(String(100), nullable=False)  # "Первый человек в космосе"
    description = Column(Text, nullable=False)  # Краткое описание
    image_url = Column(String(500))  # URL изображения
    era = Column(String(50))  # "XX век"
    tags = Column(String(200))  # "космонавт, СССР, рекорд"

    # Дополнительные данные для модального окна
    birth_date = Column(String(50))  # "9 марта 1934"
    death_date = Column(String(50))  # "27 марта 1968"
    achievements = Column(Text)  # Основные достижения
    biography = Column(Text)  # Полная биография
    is_active = Column(Boolean, default=True)  # Флаг активности


class User(Base):
    """Таблица для хранения данных пользователя"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    email = Column(String(100), nullable=False, index=True)
    phone_number = Column(String(12), nullable=False, index=True)
    password = Column(String(100), nullable=False, index=True)
