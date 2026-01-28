import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.db.database import create_db
from app.user.routers import admin_router, user_router, public_router
from app.lineevent.routers import router as line_event_router
from app.hero.routers import router as hero_router

load_dotenv()
app = FastAPI(title="Astronomy API")

app.include_router(admin_router)
app.include_router(public_router)
app.include_router(user_router)
app.include_router(line_event_router)
app.include_router(hero_router)


@app.on_event("startup")
async def startup():
    await create_db()

CORSMiddleware(
    app,
    allow_origins=["*"],
)

def main():
    uvicorn.run("main:app", port=8000)


if __name__ == "__main__":
    main()