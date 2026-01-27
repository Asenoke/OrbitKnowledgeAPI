from pydantic import BaseModel, Field


class LineEventAddSchema(BaseModel):
    year: int = Field(...)
    title: str = Field(...)
    description: str = Field(...)


class LineEventSchema(LineEventAddSchema):
    id: int