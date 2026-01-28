from fastapi import APIRouter, HTTPException, Depends
from fastapi.params import Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Annotated, List
from starlette import status

from app.db.database import get_session
from app.db.models import TimelineEventModel
from app.dependencies.dependencies import require_admin
from app.lineevent.schema import LineEventAddSchema, LineEventUpdateSchema

router = APIRouter(prefix="/lineevent", tags=["Работа с данными для ленты времени"])

SessionDep = Annotated[AsyncSession, Depends(get_session)]


@router.post("/createLineEvent", dependencies=[Depends(require_admin)])
async def create_line_event(event: LineEventAddSchema, session: SessionDep):
    """Создание нового события в ленте времени"""
    new_event = TimelineEventModel(
        year=event.year,
        title=event.title,
        description=event.description
    )
    session.add(new_event)
    await session.commit()
    await session.refresh(new_event)

    return {"success": "Новое событие для ленты времени добавлено"}


@router.get("/getAllLineEvents")
async def get_all_line_events(
        session: SessionDep,
        skip: int = Query(0, ge=0, description="Сколько событий пропустить"),
        limit: int = Query(100, ge=1, le=1000, description="Лимит событий")
):
    """Получение всех событий ленты времени с пагинацией"""
    stmt = select(TimelineEventModel).offset(skip).limit(limit)
    result = await session.execute(stmt)
    events = result.scalars().all()

    return events


@router.get("/getLineEvent/{event_id}")
async def get_line_event(event_id: int, session: SessionDep):
    """Получение события по ID"""
    stmt = select(TimelineEventModel).where(TimelineEventModel.id == event_id)
    result = await session.execute(stmt)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Событие с ID {event_id} не найдено"
        )

    return event


@router.put("/updateLineEvent/{event_id}", dependencies=[Depends(require_admin)])
async def update_line_event(event_id: int, update_event: LineEventUpdateSchema, session: SessionDep):
    """Обновление события по ID"""
    # Находим событие
    stmt = select(TimelineEventModel).where(TimelineEventModel.id == event_id)
    result = await session.execute(stmt)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Событие с ID {event_id} не найдено"
        )

    # Обновляем только указанные поля
    updated_fields = []

    if update_event.year is not None:
        event.year = update_event.year
        updated_fields.append("year")

    if update_event.title is not None:
        event.title = update_event.title
        updated_fields.append("title")

    if update_event.description is not None:
        event.description = update_event.description
        updated_fields.append("description")

    # Если ничего не обновляли, возвращаем событие без изменений
    if not updated_fields:
        return event

    await session.commit()
    await session.refresh(event)

    return event


@router.delete("/deleteLineEvent/{event_id}", dependencies=[Depends(require_admin)])
async def delete_line_event(event_id: int, session: SessionDep):
    """Удаление события по ID"""
    # Находим событие
    stmt = select(TimelineEventModel).where(TimelineEventModel.id == event_id)
    result = await session.execute(stmt)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Событие с ID {event_id} не найдено"
        )

    # Удаляем событие
    await session.delete(event)
    await session.commit()

    return {
        "status": "success",
        "message": f"Событие с ID {event_id} успешно удалено",
        "deleted_event": {
            "id": event_id,
            "year": event.year,
            "title": event.title
        }
    }


@router.get("/getEventsByYear/{year}", dependencies=[Depends(require_admin)])
async def get_events_by_year(
        year: int,
        session: SessionDep,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
):
    """Получение событий по году"""
    stmt = select(TimelineEventModel).where(TimelineEventModel.year == year).offset(skip).limit(limit)
    result = await session.execute(stmt)
    events = result.scalars().all()

    return events


@router.get("/searchEvents", dependencies=[Depends(require_admin)])
async def search_events(
        session: SessionDep,
        year: int = Query(None, description="Год события"),
        title_contains: str = Query(None, description="Часть названия"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
):
    """Поиск событий по различным критериям"""
    stmt = select(TimelineEventModel)

    # Фильтры
    if year is not None:
        stmt = stmt.where(TimelineEventModel.year == year)

    if title_contains is not None:
        stmt = stmt.where(TimelineEventModel.title.ilike(f"%{title_contains}%"))

    # Пагинация
    stmt = stmt.offset(skip).limit(limit)

    result = await session.execute(stmt)
    events = result.scalars().all()

    return events