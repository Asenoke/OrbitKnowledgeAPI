from pydantic import BaseModel, EmailStr
from typing import Optional
from enum import Enum
from datetime import datetime


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
    title: str
    description: Optional[str] = None
    project_type: ProjectType


class ProjectResponseSchema(BaseModel):
    id: int
    user_id: int
    user_name: str
    user_email: EmailStr
    user_phone: str
    title: str
    description: Optional[str]
    project_type: str
    file_name: str
    file_size: int
    status: str
    created_at: datetime
    rating: int
    votes_count: int

    class Config:
        from_attributes = True


class ProjectUpdateSchema(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    admin_comment: Optional[str] = None


class ProjectFilterSchema(BaseModel):
    status: Optional[ProjectStatus] = None
    project_type: Optional[ProjectType] = None
    user_id: Optional[int] = None
    min_rating: Optional[int] = None


