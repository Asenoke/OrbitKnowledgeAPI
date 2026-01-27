import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

from app.db.database import create_db
from app.user.routers import admin_router, user_router, public_router
from app.lineevent.routers import router as line_event_router

load_dotenv()
app = FastAPI(title="Astronomy API")

app.include_router(admin_router)
app.include_router(public_router)
app.include_router(user_router)
app.include_router(line_event_router)


@app.on_event("startup")
async def startup():
    await create_db()


def main():
    uvicorn.run("main:app", port=8000)


if __name__ == "__main__":
    main()