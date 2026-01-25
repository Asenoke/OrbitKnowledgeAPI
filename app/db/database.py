from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.db.models import Base

from config import settings



async_engine = create_async_engine(url=settings.DB_URL, echo=True)
async_session = async_sessionmaker(bind=async_engine, expire_on_commit=False, class_=AsyncSession)



async def create_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session():
    async with async_session() as session:
        yield session