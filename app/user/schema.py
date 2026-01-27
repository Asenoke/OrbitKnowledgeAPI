import enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"


class UserAddSchema(BaseModel):
    name: str = Field(..., max_length=20, min_length=1)
    email: EmailStr = Field(...)
    phone_number: str = Field(..., min_length=8, max_length=20)
    password: str = Field(..., min_length=8)

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        cleaned = v

        if cleaned.startswith('+'):
            cleaned = cleaned[1:]

        for char in [' ', '-', '(', ')', '.']:
            cleaned = cleaned.replace(char, '')

        if not cleaned.isdigit():
            raise ValueError('Phone number must contain only digits')

        return cleaned


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)


class UserUpdateSchema(BaseModel):
    name: Optional[str] = Field(None, max_length=100, min_length=1)
    phone_number: Optional[str] = Field(None, min_length=8, max_length=20)
    password: Optional[str] = Field(None, min_length=8)

    @field_validator('phone_number')
    @classmethod
    def validate_phone_number(cls, v):
        if v is None:
            return v

        cleaned = v
        if cleaned.startswith('+'):
            cleaned = cleaned[1:]

        for char in [' ', '-', '(', ')', '.']:
            cleaned = cleaned.replace(char, '')

        if not cleaned.isdigit():
            raise ValueError('Phone number must contain only digits')

        return cleaned