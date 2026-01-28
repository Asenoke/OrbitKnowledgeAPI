from pydantic import BaseModel, Field


class HeroAddSchema(BaseModel):
    name: str = Field(..., max_length=100)
    role: str = Field(..., max_length=100)
    description: str = Field(...)
    image_url: str = Field(None, max_length=500)
    era: str = Field(None, max_length=50)
    tags: str = Field(None, max_length=200)
    birth_date: str = Field(None, max_length=50)
    death_date: str = Field(None, max_length=50)
    achievements: str = None
    biography: str = None


class HeroUpdateSchema(BaseModel):
        name: str = Field(None, max_length=100)
        role: str = Field(None, max_length=100)
        description: str = Field(None)
        image_url: str = Field(None, max_length=500)
        era: str = Field(None, max_length=50)
        tags: str = Field(None, max_length=200)
        birth_date: str = Field(None, max_length=50)
        death_date: str = Field(None, max_length=50)
        achievements: str = None
        biography: str = None