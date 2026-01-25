import dotenv
import uvicorn
from fastapi import FastAPI

from app.db.database import create_db
from app.user.routers import router as user_router

dotenv.load_dotenv()
app = FastAPI(title="Astronomy API")

app.include_router(user_router)


@app.on_event("startup")
async def startup():
    await create_db()


def main():
    uvicorn.run("main:app", port=8000)


if __name__ == "__main__":
    main()