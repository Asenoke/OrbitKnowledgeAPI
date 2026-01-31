from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.db.models import Base

from config import settings


# Создание экземпляра класса асинхронного движка и асинхронной сессии
async_engine = create_async_engine(url=settings.DB_URL, echo=True)
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)


# Функция создания таблиц в базе данных
async def create_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Функция получения сессии
async def get_session():
    async with async_session() as session:
        yield session