from pydantic import BaseModel, EmailStr, Field


class UserAddSchema(BaseModel):
    name: str = Field(..., max_length=20, min_length=1)
    email: EmailStr = Field(...)
    phone_number: str = Field(..., min_length=8, max_length=20)
    password: str = Field(..., min_length=8)


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(...)
    password: str = Field(...)