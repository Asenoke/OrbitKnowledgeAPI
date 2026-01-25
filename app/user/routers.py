from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sqlalchemy import select

from app.user.schema import UserAdd
from app.db.database import get_session
from app.db.models import UserModel

router = APIRouter(tags=["Работа с пользователями"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]



@router.post("/create_user")
async def create_user(user: UserAdd, session: SessionDep):
    # Проверяем, существует ли пользователь с таким email
    existing_user = await session.execute(
        select(UserModel).where(UserModel.email == user.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Создаем объект для БД (SQLAlchemy модель)
    new_user = UserModel(
        name=user.name,
        email=user.email,
        password=user.password,
        phone_number=user.phone_number,
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)


    return {"success": True}


@router.get("/users")
async def get_all_users(session: SessionDep):
    result = await session.execute(select(UserModel))
    users = result.scalars().all()
    return users


@router.get("/users/{user_id}")
async def get_user(user_id: int, session: SessionDep):
    result = await session.execute(
        select(UserModel).where(UserModel.id == user_id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="user not found")

    return user


