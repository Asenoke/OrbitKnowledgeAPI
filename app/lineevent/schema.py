from typing import Optional
from pydantic import BaseModel, Field, field_validator

# Схема для добавления нового события ленты времени
class LineEventAddSchema(BaseModel):
    year: int = Field(...)
    title: str = Field(..., max_length=200)
    description: str = Field(...)

    @field_validator('year')
    @classmethod
    def validate_year(cls, v):
        if v < 1000 or v > 3000:
            raise ValueError('Год должен быть в диапазоне от 1000 до 3000')
        return v

# Схема для обновления события ленты времени
class LineEventUpdateSchema(BaseModel):
    year: Optional[int] = Field(None, description="Год события")
    title: Optional[str] = Field(None, max_length=200, description="Заголовок события")
    description: Optional[str] = Field(None, description="Описание события")

    @field_validator('year')
    @classmethod
    def validate_year(cls, v):
        if v is not None:
            if v < 1000 or v > 3000:
                raise ValueError('Год должен быть в диапазоне от 1000 до 3000')
        return v
