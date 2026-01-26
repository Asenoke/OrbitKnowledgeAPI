from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from starlette import status

from app.db.database import get_session
from app.db.models import UserModel
from app.security.security import hash_password, verify_password
from app.user.schema import UserAddSchema, UserLoginSchema

router = APIRouter(prefix="/user", tags=["Работа с пользователем"])

sessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserAddSchema, session: sessionDep):  # Используем UserAddSchema вместо UserSchema
    # Проверяем, существует ли пользователь с таким email
    existing_user = await session.execute(
        UserModel.__table__.select().where(UserModel.email == user.email)
    )
    if existing_user.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    existing_phone = await session.execute(
        UserModel.__table__.select().where(UserModel.phone_number == user.phone_number)
    )
    if existing_phone.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким номером телефона уже существует"
        )

    # Создаем нового пользователя
    new_user = UserModel(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        phone_number=user.phone_number,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return {
        "status": "success",
        "message": "Пользователь успешно зарегистрирован",
        "user_id": new_user.id
    }


@router.post("/login")
async def login(user: UserLoginSchema, session: sessionDep):
    # Ищем пользователя по email
    stmt = select(UserModel).where(UserModel.email == user.email)
    result = await session.execute(stmt)
    db_user = result.scalar_one_or_none()

    # Если пользователь не найден ИЛИ пароль неверный
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )

    # Возвращаем успешный ответ
    return {
        "status": "success",
        "message": "Вход выполнен успешно",
        "user_id": db_user.id,
        "name": db_user.name,
        "email": db_user.email
    }


