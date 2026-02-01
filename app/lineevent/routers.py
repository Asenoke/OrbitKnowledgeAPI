from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy import select
from starlette import status
from app.db.models import TimelineEventModel
from app.dependencies.dependencies import require_admin
from app.lineevent.schema import LineEventAddSchema, LineEventUpdateSchema
from app import SessionDep

# Создание роутера для работы с событиями ленты времени
router = APIRouter(prefix="/lineevent", tags=["Работа с данными для ленты времени"])

# Эндпоинт для создания нового события (только для админов)
@router.post("/createLineEvent", dependencies=[Depends(require_admin)])
async def create_line_event(event: LineEventAddSchema, session: SessionDep):
    new_event = TimelineEventModel(
        year=event.year,
        title=event.title,
        description=event.description
    )
    session.add(new_event)
    await session.commit()
    await session.refresh(new_event)

    return {"success": "Новое событие для ленты времени добавлено"}

# Эндпоинт для получения всех событий с пагинацией
@router.get("/getAllLineEvents")
async def get_all_line_events(
        session: SessionDep,
        skip: int = Query(0, ge=0, description="Сколько событий пропустить"),
        limit: int = Query(100, ge=1, le=1000, description="Лимит событий")
):
    stmt = select(TimelineEventModel).offset(skip).limit(limit)
    result = await session.execute(stmt)
    events = result.scalars().all()

    return events

# Эндпоинт для получения события по ID
@router.get("/getLineEvent/{event_id}")
async def get_line_event(event_id: int, session: SessionDep):
    stmt = select(TimelineEventModel).where(TimelineEventModel.id == event_id)
    result = await session.execute(stmt)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Событие с ID {event_id} не найдено"
        )

    return event

# Эндпоинт для обновления события по ID (только для админов)
@router.put("/updateLineEvent/{event_id}", dependencies=[Depends(require_admin)])
async def update_line_event(event_id: int, update_event: LineEventUpdateSchema, session: SessionDep):
    stmt = select(TimelineEventModel).where(TimelineEventModel.id == event_id)
    result = await session.execute(stmt)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Событие с ID {event_id} не найдено"
        )

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

    if not updated_fields:
        return event

    await session.commit()
    await session.refresh(event)

    return event

# Эндпоинт для удаления события по ID (только для админов)
@router.delete("/deleteLineEvent/{event_id}", dependencies=[Depends(require_admin)])
async def delete_line_event(event_id: int, session: SessionDep):
    stmt = select(TimelineEventModel).where(TimelineEventModel.id == event_id)
    result = await session.execute(stmt)
    event = result.scalar_one_or_none()

    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Событие с ID {event_id} не найдено"
        )

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

# Эндпоинт для получения событий по году (только для админов)
@router.get("/getEventsByYear/{year}", dependencies=[Depends(require_admin)])
async def get_events_by_year(
        year: int,
        session: SessionDep,
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
):
    # ОШИБКА: год в базе хранится как String, а запрос принимает int
    stmt = select(TimelineEventModel).where(TimelineEventModel.year == str(year)).offset(skip).limit(limit)
    result = await session.execute(stmt)
    events = result.scalars().all()

    return events

# Эндпоинт для поиска событий по различным критериям (только для админов)
@router.get("/searchEvents", dependencies=[Depends(require_admin)])
async def search_events(
        session: SessionDep,
        year: int = Query(None, description="Год события"),
        title_contains: str = Query(None, description="Часть названия"),
        skip: int = Query(0, ge=0),
        limit: int = Query(100, ge=1, le=1000)
):
    stmt = select(TimelineEventModel)

    if year is not None:
        stmt = stmt.where(TimelineEventModel.year == str(year))

    if title_contains is not None:
        stmt = stmt.where(TimelineEventModel.title.ilike(f"%{title_contains}%"))

    stmt = stmt.offset(skip).limit(limit)

    result = await session.execute(stmt)
    events = result.scalars().all()

    return events
