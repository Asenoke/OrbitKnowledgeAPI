from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from typing import List
from app.security.security import verify_token
from app.db.database import get_session
from app.db.models import UserModel, UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

# создание экземпляра HTTPBearer
security = HTTPBearer()

# Функция (зависимость) для получения текущего пользователя
async def get_current_user(
        credentials=Depends(security),
        session: AsyncSession = Depends(get_session)
) -> UserModel:

    token = credentials.credentials

    payload = verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"}
        )

    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные данные в токене"
        )

    stmt = select(UserModel).where(UserModel.id == user_id)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )

    return user

# функция (зависимость) для проверки роли
def require_role(required_role: UserRole):
    async def role_checker(current_user: UserModel = Depends(get_current_user)):
        if current_user.role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется роль {required_role.value}"
            )
        return current_user

    return role_checker


# Функция проверки на одну из нескольких ролей
def require_any_role(allowed_roles: List[UserRole]):
    async def role_checker(current_user: UserModel = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Требуется одна из ролей: {', '.join([r.value for r in allowed_roles])}"
            )
        return current_user

    return role_checker


# Объявление
require_admin = require_role(UserRole.ADMIN)
require_user = require_role(UserRole.USER)
require_admin_or_user = require_any_role([UserRole.ADMIN, UserRole.USER])