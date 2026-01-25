from pydantic import BaseModel, EmailStr


class UserAdd(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    password: str

class UserSchema(UserAdd):
    id: int