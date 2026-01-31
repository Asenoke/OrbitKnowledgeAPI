from fastapi import APIRouter, HTTPException, Depends
from fastapi.params import Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from starlette import status

from app.db.database import get_session
from app.db.models import UserModel, UserRole
from app.security.security import hash_password, verify_password, create_access_token
from app.user.schema import UserAddSchema, UserLoginSchema, UserUpdateSchema
from app.dependencies.dependencies import get_current_user, require_admin, require_admin_or_user

# Публичные роутеры (доступны всем)
public_router = APIRouter(prefix="/user", tags=["Публичные методы"])

# Роутеры для обычных пользователей и администраторов (оба могут получить доступ)
user_router = APIRouter(prefix="/user", tags=["Методы пользователя"], dependencies=[Depends(require_admin_or_user)])

# Роутеры только для администраторов
admin_router = APIRouter(prefix="/user/admin", tags=["Методы администратора"], dependencies=[Depends(require_admin)])

sessionDep = Annotated[AsyncSession, Depends(get_session)]


# ============ ПУБЛИЧНЫЕ ЭНДПОИНТЫ (доступны всем) ============

@public_router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(user: UserAddSchema, session: sessionDep):
    """Регистрация нового пользователя (по умолчанию роль USER)"""
    # Проверяем, существует ли пользователь с таким email
    existing_user = await session.execute(
        select(UserModel).where(UserModel.email == user.email)
    )
    if existing_user.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )

    existing_phone = await session.execute(
        select(UserModel).where(UserModel.phone_number == user.phone_number)
    )
    if existing_phone.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким номером телефона уже существует"
        )

    # Создаем нового пользователя с ролью USER по умолчанию
    new_user = UserModel(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        phone_number=user.phone_number,
        role=UserRole.USER
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return {
        "status": "success",
        "message": "Пользователь успешно зарегистрирован",
        "user_id": new_user.id,
        "role": new_user.role.value
    }


@public_router.post("/login")
async def login(user: UserLoginSchema, session: sessionDep):
    """Вход в систему"""
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

    # Создаем JWT токен с информацией о роли
    access_token = create_access_token(
        data={
            "sub": db_user.email,
            "user_id": db_user.id,
            "name": db_user.name,
            "role": db_user.role.value
        }
    )

    # Возвращаем токен с ролью
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": db_user.role.value
    }


@public_router.post("/logout")
async def logout():
    """Выход из системы (клиентская операция)"""
    return {
        "status": "success",
        "message": "Вы вышли из аккаунта"
    }


# ============ ЭНДПОИНТЫ ДЛЯ ОБЫЧНЫХ ПОЛЬЗОВАТЕЛЕЙ И АДМИНОВ ============

@user_router.get("/profile")
async def get_profile(current_user: UserModel = Depends(get_current_user)):
    """Получение профиля текущего пользователя"""
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "role": current_user.role.value
    }


@user_router.put("/profile")
async def update_profile(
        update_data: UserUpdateSchema,
        session: sessionDep,
        current_user: UserModel = Depends(get_current_user),

):
    """Обновление профиля пользователя"""
    # Обновляем только предоставленные поля
    if update_data.name is not None:
        current_user.name = update_data.name

    if update_data.phone_number is not None:
        # Проверяем уникальность номера телефона
        existing_phone = await session.execute(
            select(UserModel).where(
                UserModel.phone_number == update_data.phone_number,
                UserModel.id != current_user.id
            )
        )
        if existing_phone.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Этот номер телефона уже используется"
            )
        current_user.phone_number = update_data.phone_number

    # Обновление пароля (если предоставлен)
    if update_data.password is not None:
        current_user.password = hash_password(update_data.password)

    await session.commit()
    await session.refresh(current_user)

    return {
        "status": "success",
        "message": "Профиль обновлен",
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "phone_number": current_user.phone_number,
            "role": current_user.role.value
        }
    }


@user_router.delete("/profile")
async def delete_profile(
        session: sessionDep,
        current_user: UserModel = Depends(get_current_user)

):
    """Удаление своего профиля"""
    await session.delete(current_user)
    await session.commit()

    return {
        "status": "success",
        "message": "Ваш профиль удален"
    }


# ============ ЭНДПОИНТЫ ТОЛЬКО ДЛЯ АДМИНИСТРАТОРОВ ============
@admin_router.get("/users")
async def get_all_users(
        session: sessionDep,
        current_user: UserModel = Depends(require_admin),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
):
    """Получение списка всех пользователей (только для администраторов)"""
    stmt = select(UserModel).offset(skip).limit(limit)
    result = await session.execute(stmt)
    users = result.scalars().all()

    # Форматируем ответ
    return [
        {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone_number": user.phone_number,
            "role": user.role.value
        }
        for user in users
    ]


@admin_router.get("/users/{user_id}")
async def get_user_by_id(
        user_id: int,
        session: sessionDep,
        current_user: UserModel = Depends(require_admin)
):
    """Получение информации о любом пользователе по ID"""
    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone_number": user.phone_number,
        "role": user.role.value
    }


@admin_router.put("/users/{user_id}/role")
async def change_user_role(
        user_id: int,
        new_role: UserRole,
        session: sessionDep,
        current_user: UserModel = Depends(require_admin)
):
    """Изменение роли пользователя (только для администраторов)"""
    # Администратор не может изменить свою собственную роль
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы не можете изменить свою собственную роль"
        )

    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )

    # Изменяем роль
    user.role = new_role
    await session.commit()

    return {
        "status": "success",
        "message": f"Роль пользователя {user_id} изменена на {new_role.value}",
        "user_id": user_id,
        "new_role": new_role.value
    }


@admin_router.delete("/users/{user_id}")
async def delete_user(
        user_id: int,
        session: sessionDep,
        current_user: UserModel = Depends(require_admin)
):
    """Удаление любого пользователя (только для администраторов)"""
    # Администратор не может удалить себя
    if user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы не можете удалить свой собственный аккаунт"
        )

    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Пользователь с ID {user_id} не найден"
        )

    await session.delete(user)
    await session.commit()

    return {
        "status": "success",
        "message": f"Пользователь с ID {user_id} удален"
    }


@admin_router.get("/statistics")
async def get_statistics(
        session: sessionDep,
        current_user: UserModel = Depends(require_admin)
):
    """Статистика пользователей (только для администраторов)"""
    # Общее количество пользователей
    total_users_stmt = select(UserModel)
    total_users_result = await session.execute(total_users_stmt)
    total_users = len(total_users_result.scalars().all())

    # Количество администраторов
    admins_stmt = select(UserModel).where(UserModel.role == UserRole.ADMIN)
    admins_result = await session.execute(admins_stmt)
    admin_count = len(admins_result.scalars().all())

    # Количество обычных пользователей
    user_count = total_users - admin_count

    return {
        "total_users": total_users,
        "admins": admin_count,
        "users": user_count,
        "admin_percentage": round((admin_count / total_users * 100), 2) if total_users > 0 else 0
    }