from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.db.models import Base
from config import settings

# Создание асинхронного движка для подключения к базе данных
async_engine = create_async_engine(url=settings.DB_URL, echo=True)

# Создание фабрики асинхронных сессий
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)

# Функция создания всех таблиц в базе данных
async def create_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Функция-зависимость для получения сессии базы данных
async def get_session():
    async with async_session() as session:
        yield session
