from pydantic import BaseModel, Field, validator
from typing import Optional
from enum import Enum


class ProjectStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FEATURED = "featured"


class ProjectType(str, Enum):
    DRAWING = "drawing"
    PROJECT = "project"
    IDEA = "idea"


class ProjectCreateSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    project_type: ProjectType


class ProjectUpdateSchema(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=5000)
    status: Optional[str] = None  # Изменил на str для гибкости
    admin_comment: Optional[str] = Field(None, max_length=1000)
    rating: Optional[int] = Field(None, ge=-100, le=100)

    @validator('status')
    def validate_status(cls, v):
        if v is None:
            return v
        v_lower = v.lower()
        valid_statuses = ["pending", "approved", "rejected", "featured"]
        if v_lower not in valid_statuses:
            raise ValueError(f"Недопустимый статус. Допустимые значения: {', '.join(valid_statuses)}")
        return v_lower


class ProjectFilterSchema(BaseModel):
    status: Optional[str] = None  # Изменил на str
    project_type: Optional[str] = None  # Изменил на str
    user_id: Optional[int] = None
    min_rating: Optional[int] = None
    search: Optional[str] = None




class VoteSchema(BaseModel):
    vote: int = Field(1, ge=-1, le=1, description="-1 - против, 0 - убрать голос, 1 - за")



class StatsResponse(BaseModel):
    total_projects: int
    status_distribution: dict
    type_distribution: dict
    total_votes: int
    total_rating: int
    average_rating: float