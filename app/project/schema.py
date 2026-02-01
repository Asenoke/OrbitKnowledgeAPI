from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum


class ProjectStatus(str, Enum):
    # Перечисление статусов проекта
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FEATURED = "featured"


class ProjectType(str, Enum):
    # Перечисление типов проектов
    DRAWING = "drawing"
    PROJECT = "project"
    IDEA = "idea"


class ProjectCreateSchema(BaseModel):
    # Схема для создания проекта
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    project_type: ProjectType


class ProjectUpdateSchema(BaseModel):
    # Схема для обновления проекта
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[str] = None
    admin_comment: Optional[str] = None
    rating: Optional[int] = Field(None, ge=0, le=100)

    @validator('status')
    def validate_status(cls, v):
        # Валидатор для статуса проекта
        if v is None:
            return v
        v_upper = v.upper()  # Приводим к верхнему регистру для совместимости с БД
        valid_statuses = ["PENDING", "APPROVED", "REJECTED", "FEATURED"]
        if v_upper not in valid_statuses:
            raise ValueError(f"Недопустимый статус. Допустимые значения: {', '.join(valid_statuses)}")
        return v_upper


class ProjectFilterSchema(BaseModel):
    # Схема для фильтрации проектов
    status: Optional[str] = None
    project_type: Optional[str] = None
    user_id: Optional[int] = None
    min_rating: Optional[int] = None
    search: Optional[str] = None


class ProjectStatusUpdateSchema(BaseModel):
    # Специальная схема для обновления статуса
    status: str = Field(..., description="Новый статус проекта")

    @validator('status')
    def validate_status(cls, v):
        v_upper = v.upper()
        valid_statuses = ["PENDING", "APPROVED", "REJECTED", "FEATURED"]
        if v_upper not in valid_statuses:
            raise ValueError(f"Недопустимый статус. Допустимые значения: {', '.join(valid_statuses)}")
        return v_upper


class VoteSchema(BaseModel):
    # Схема для голосования
    vote: int = Field(1, ge=-1, le=1, description="-1 - против, 0 - убрать голос, 1 - за")


class StatsResponse(BaseModel):
    # Схема для ответа со статистикой
    total_projects: int
    status_distribution: dict
    type_distribution: dict
    total_votes: int
    total_rating: int
    average_rating: float
