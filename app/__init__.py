from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from app.db.database import get_session


SessionDep = Annotated[AsyncSession, Depends(get_session)]
