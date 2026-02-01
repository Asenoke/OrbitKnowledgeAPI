from fastapi import APIRouter, Depends, Form, UploadFile, File, HTTPException, Query
from sqlalchemy import select, func, or_
import os
import uuid

from app import SessionDep
from app.db.models import UserModel, ProjectModel, UserRole
from app.dependencies.dependencies import require_admin_or_user

projects_router = APIRouter(prefix="/projects", tags=["Проекты КБ Будущего"])

UPLOAD_DIR = "uploads/projects"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ============ ПРОСТЫЕ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============

def project_to_response(project):
    """Преобразование модели в словарь"""
    return {
        "id": project.id,
        "user_id": project.user_id,
        "user_name": project.user_name,
        "user_email": project.user_email,
        "title": project.title,
        "description": project.description,
        "project_type": project.project_type,
        "file_path": project.file_path,
        "file_name": project.file_name,
        "file_size": project.file_size,
        "status": project.status.lower() if project.status else "pending",
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "admin_comment": project.admin_comment,
        "rating": project.rating or 0,
        "votes_count": project.votes_count or 0
    }


def check_user_access(project, user):
    """Проверка прав доступа"""
    if user.role != UserRole.ADMIN and project.user_id != user.id:
        raise HTTPException(status_code=403, detail="Недостаточно прав")


# ============ ОСНОВНЫЕ ЭНДПОИНТЫ ============

@projects_router.post("/upload")
async def upload_project(
        session: SessionDep,
        title: str = Form(...),
        description: str = Form(None),
        project_type: str = Form(...),
        file: UploadFile = File(...),
        current_user: UserModel = Depends(require_admin_or_user)
):
    """Загрузка нового проекта"""
    # Сохраняем файл
    file_content = await file.read()
    file_size = len(file_content)

    # Генерируем уникальное имя файла
    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Сохраняем файл
    with open(file_path, "wb") as buffer:
        buffer.write(file_content)

    # Создаем проект
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
        status="PENDING",  # Строка, а не enum
        rating=0,
        votes_count=0
    )

    session.add(project)
    await session.commit()
    await session.refresh(project)

    return {"message": "Проект загружен", "project_id": project.id, "project": project_to_response(project)}


@projects_router.get("/")
async def get_projects(
        session: SessionDep,
        status: str = Query(None),
        project_type: str = Query(None),
        search: str = Query(None),
        limit: int = Query(100, ge=1, le=1000),
        offset: int = Query(0, ge=0)
):
    """Получение списка проектов"""
    query = select(ProjectModel)

    # Фильтр по статусу (статус в базе - строка в верхнем регистре)
    if status and status.strip():
        # Приводим входной статус к верхнему регистру
        status_filter = status.strip().upper()
        query = query.where(ProjectModel.status == status_filter)

    # Фильтр по типу проекта
    if project_type and project_type.strip():
        query = query.where(ProjectModel.project_type == project_type.strip())

    # Фильтр по поиску
    if search and search.strip():
        search_term = f"%{search.strip()}%"
        query = query.where(
            or_(
                ProjectModel.title.ilike(search_term),
                ProjectModel.description.ilike(search_term)
            )
        )

    # Получаем общее количество с учетом фильтров
    count_query = select(func.count()).select_from(ProjectModel)

    if status and status.strip():
        status_filter = status.strip().upper()
        count_query = count_query.where(ProjectModel.status == status_filter)

    if project_type and project_type.strip():
        count_query = count_query.where(ProjectModel.project_type == project_type.strip())

    if search and search.strip():
        search_term = f"%{search.strip()}%"
        count_query = count_query.where(
            or_(
                ProjectModel.title.ilike(search_term),
                ProjectModel.description.ilike(search_term)
            )
        )

    total_count = await session.scalar(count_query) or 0

    # Сортировка (сначала featured, потом новые)
    query = query.order_by(
        # Сначала featured проекты
        func.nullif(ProjectModel.status == "FEATURED", False).desc(),
        ProjectModel.created_at.desc()
    ).offset(offset).limit(limit)

    result = await session.execute(query)
    projects = result.scalars().all()

    return {
        "projects": [project_to_response(p) for p in projects],
        "total": total_count,
        "limit": limit,
        "offset": offset
    }


@projects_router.get("/{project_id}")
async def get_project(project_id: int, session: SessionDep):
    """Получение проекта по ID"""
    result = await session.execute(select(ProjectModel).where(ProjectModel.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    return project_to_response(project)


@projects_router.get("/my/projects")
async def get_my_projects(
        session: SessionDep,
        current_user: UserModel = Depends(require_admin_or_user)
):
    """Получение проектов текущего пользователя"""
    query = select(ProjectModel).where(ProjectModel.user_id == current_user.id)
    result = await session.execute(query.order_by(ProjectModel.created_at.desc()))
    projects = result.scalars().all()

    return [project_to_response(p) for p in projects]


@projects_router.put("/{project_id}")
async def update_project(
        project_id: int,
        session: SessionDep,
        title: str = Form(None),
        description: str = Form(None),
        current_user: UserModel = Depends(require_admin_or_user)
):
    """Обновление проекта"""
    result = await session.execute(select(ProjectModel).where(ProjectModel.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    # Проверка прав
    check_user_access(project, current_user)

    # Обновление
    if title:
        project.title = title.strip()
    if description is not None:
        project.description = description.strip() if description else None

    await session.commit()

    return {"message": "Проект обновлен", "project": project_to_response(project)}


@projects_router.patch("/{project_id}/status")
async def update_status(
        project_id: int,
        status: str,
        session: SessionDep,
        current_user: UserModel = Depends(require_admin_or_user)
):
    """Обновление статуса (только админ)"""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Только для администратора")

    result = await session.execute(select(ProjectModel).where(ProjectModel.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    # Проверка статуса
    valid_statuses = ["PENDING", "APPROVED", "REJECTED", "FEATURED"]
    status_upper = status.strip().upper()

    if status_upper not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Неверный статус. Допустимые: {', '.join(valid_statuses)}")

    project.status = status_upper  # Просто строка
    await session.commit()

    return {"message": "Статус обновлен", "project": project_to_response(project)}


@projects_router.delete("/{project_id}")
async def delete_project(
        project_id: int,
        session: SessionDep,
        current_user: UserModel = Depends(require_admin_or_user)
):
    """Удаление проекта"""
    result = await session.execute(select(ProjectModel).where(ProjectModel.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    # Проверка прав
    check_user_access(project, current_user)

    # Удаляем файл
    try:
        if project.file_path and os.path.exists(project.file_path):
            os.remove(project.file_path)
    except Exception as e:
        print(f"Ошибка при удалении файла: {e}")

    await session.delete(project)
    await session.commit()

    return {"message": "Проект удален"}


@projects_router.post("/{project_id}/vote")
async def vote_for_project(
        project_id: int,
        vote: int,
        session: SessionDep,
        current_user: UserModel = Depends(require_admin_or_user)
):
    """Голосование за проект"""
    result = await session.execute(select(ProjectModel).where(ProjectModel.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")

    # Проверяем, что проект одобрен или featured
    if project.status not in ["APPROVED", "FEATURED"]:
        raise HTTPException(status_code=400, detail="Можно голосовать только за одобренные проекты")

    # Проверяем, что пользователь не голосует за свой проект
    if project.user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя голосовать за свой проект")

    # Обновляем рейтинг
    project.rating = (project.rating or 0) + vote
    project.votes_count = (project.votes_count or 0) + 1

    await session.commit()

    return {
        "message": "Голос учтен",
        "rating": project.rating,
        "votes_count": project.votes_count
    }


@projects_router.get("/stats/summary")
async def get_stats(session: SessionDep):
    """Статистика проектов"""
    # Общее количество
    total = await session.scalar(select(func.count(ProjectModel.id))) or 0

    # По статусам
    pending = await session.scalar(select(func.count()).where(ProjectModel.status == "PENDING")) or 0
    approved = await session.scalar(select(func.count()).where(ProjectModel.status == "APPROVED")) or 0
    rejected = await session.scalar(select(func.count()).where(ProjectModel.status == "REJECTED")) or 0
    featured = await session.scalar(select(func.count()).where(ProjectModel.status == "FEATURED")) or 0

    # Общий рейтинг
    total_rating = await session.scalar(select(func.sum(ProjectModel.rating))) or 0
    total_votes = await session.scalar(select(func.sum(ProjectModel.votes_count))) or 0

    # Проекты по типам
    types_result = await session.execute(
        select(ProjectModel.project_type, func.count(ProjectModel.id))
        .group_by(ProjectModel.project_type)
    )
    type_distribution = {str(t): c for t, c in types_result.all() if t}

    return {
        "total_projects": total,
        "status_distribution": {
            "pending": pending,
            "approved": approved,
            "rejected": rejected,
            "featured": featured
        },
        "type_distribution": type_distribution,
        "total_rating": total_rating,
        "total_votes": total_votes,
        "average_rating": round(total_rating / total_votes, 2) if total_votes > 0 else 0
    }