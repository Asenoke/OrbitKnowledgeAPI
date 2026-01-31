import os
import uuid
from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.db.database import get_session
from app.db.models import UserModel, ProjectModel, ProjectStatus, UserRole
from app.dependencies.dependencies import require_admin_or_user
from app.project.schema import ProjectUpdateSchema, ProjectResponseSchema

# Роутер для проектов
projects_router = APIRouter(prefix="/projects", tags=["Проекты КБ Будущего"])

sessionDep = Annotated[AsyncSession, Depends(get_session)]

# Настройки для загрузки файлов
UPLOAD_DIR = "uploads/projects"
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.pdf', '.doc', '.docx', '.txt', '.zip', '.rar'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Создаем директорию для загрузок, если её нет
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============ РОУТЕРЫ ДЛЯ ПРОЕКТОВ ============

# Загрузка проекта (требуется авторизация)
@projects_router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_project(
        session: sessionDep,
        title: str = Form(...),
        description: Optional[str] = Form(None),
        project_type: str = Form(...),
        file: UploadFile = File(...),
        current_user: UserModel = Depends(require_admin_or_user)
):
    # Проверяем размер файла
    file.file.seek(0, 2)  # Перемещаемся в конец файла
    file_size = file.file.tell()
    file.file.seek(0)  # Возвращаемся в начало

    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Файл слишком большой. Максимальный размер: {MAX_FILE_SIZE // (1024 * 1024)}MB"
        )

    # Проверяем расширение файла
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Недопустимый тип файла. Разрешены: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Генерируем уникальное имя файла
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Сохраняем файл
    try:
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при сохранении файла: {str(e)}"
        )

    # Создаем запись в базе данных
    project = ProjectModel(
        user_id=current_user.id,
        user_name=current_user.name,
        user_email=current_user.email,
        user_phone=current_user.phone_number,
        title=title,
        description=description,
        project_type=project_type,
        file_path=file_path,
        file_name=file.filename,
        file_size=file_size,
        status=ProjectStatus.PENDING
    )

    session.add(project)
    await session.commit()
    await session.refresh(project)

    return {
        "status": "success",
        "message": "Проект успешно загружен",
        "project_id": project.id,
        "file_name": file.filename
    }


# Получение списка проектов (публичный доступ)
@projects_router.get("/")
async def get_projects(
        session: sessionDep,
        status: Optional[ProjectStatus] = Query(None),
        project_type: Optional[str] = Query(None),
        limit: int = Query(50, ge=1, le=100),
        offset: int = Query(0, ge=0)
):
    query = select(ProjectModel).where(ProjectModel.status != ProjectStatus.REJECTED)

    if status:
        query = query.where(ProjectModel.status == status)
    if project_type:
        query = query.where(ProjectModel.project_type == project_type)

    query = query.order_by(ProjectModel.created_at.desc()).offset(offset).limit(limit)

    result = await session.execute(query)
    projects = result.scalars().all()

    return projects


# Получение проекта по ID (публичный доступ)
@projects_router.get("/{project_id}")
async def get_project(
        project_id: int,
        session: sessionDep
):
    query = select(ProjectModel).where(ProjectModel.id == project_id)
    result = await session.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )

    return project


# Получение моих проектов (требуется авторизация)
@projects_router.get("/my/projects")
async def get_my_projects(
        session: sessionDep,
        current_user: UserModel = Depends(require_admin_or_user),
        status: Optional[ProjectStatus] = Query(None),
        limit: int = Query(20, ge=1, le=50),
        offset: int = Query(0, ge=0)
):
    query = select(ProjectModel).where(ProjectModel.user_id == current_user.id)

    if status:
        query = query.where(ProjectModel.status == status)

    query = query.order_by(ProjectModel.created_at.desc()).offset(offset).limit(limit)

    result = await session.execute(query)
    projects = result.scalars().all()

    return projects


# Обновление проекта (только владелец или админ)
@projects_router.put("/{project_id}")
async def update_project(
        project_id: int,
        update_data: ProjectUpdateSchema,
        session: sessionDep,
        current_user: UserModel = Depends(require_admin_or_user)
):
    query = select(ProjectModel).where(ProjectModel.id == project_id)
    result = await session.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )

    # Проверяем права доступа
    if current_user.role != UserRole.ADMIN and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для редактирования этого проекта"
        )

    # Обновляем данные
    if update_data.title is not None:
        project.title = update_data.title
    if update_data.description is not None:
        project.description = update_data.description
    if update_data.status is not None and current_user.role == UserRole.ADMIN:
        project.status = update_data.status
    if update_data.admin_comment is not None and current_user.role == UserRole.ADMIN:
        project.admin_comment = update_data.admin_comment

    project.updated_at = datetime.utcnow()

    await session.commit()
    await session.refresh(project)

    return {
        "status": "success",
        "message": "Проект обновлен",
        "project": ProjectResponseSchema.from_orm(project)
    }


# Удаление проекта (только владелец или админ)
@projects_router.delete("/{project_id}")
async def delete_project(
        project_id: int,
        session: sessionDep,
        current_user: UserModel = Depends(require_admin_or_user)
):
    query = select(ProjectModel).where(ProjectModel.id == project_id)
    result = await session.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )

    # Проверяем права доступа
    if current_user.role != UserRole.ADMIN and project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления этого проекта"
        )

    # Удаляем файл
    try:
        if os.path.exists(project.file_path):
            os.remove(project.file_path)
    except Exception as e:
        print(f"Ошибка при удалении файла: {str(e)}")

    # Удаляем запись из базы
    await session.delete(project)
    await session.commit()

    return {
        "status": "success",
        "message": "Проект удален"
    }


# Голосование за проект (требуется авторизация)
@projects_router.post("/{project_id}/vote")
async def vote_for_project(
        session: sessionDep,
        project_id: int,
        vote: int = Query(1, ge=-1, le=1),  # -1, 0, 1
        current_user: UserModel = Depends(require_admin_or_user)
):
    query = select(ProjectModel).where(ProjectModel.id == project_id)
    result = await session.execute(query)
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Проект не найден"
        )

    # Проверяем, что пользователь не голосует за свой проект
    if project.user_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя голосовать за свой собственный проект"
        )

    # Обновляем рейтинг (упрощенная логика)
    project.rating += vote
    project.votes_count += 1

    await session.commit()

    return {
        "status": "success",
        "message": "Ваш голос учтен",
        "new_rating": project.rating,
        "votes_count": project.votes_count
    }

