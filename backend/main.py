from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.db import engine, get_session
from backend.models import Base
from backend.api import user_router, pa_router
from backend.repositories import UserRepository
import os
from dotenv import load_dotenv
import logging

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(user_router)
app.include_router(pa_router)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_default_admin():
    admin_email = os.getenv("ADMIN_EMAIL")
    admin_password = os.getenv("ADMIN_PASSWORD")

    if not admin_email or not admin_password:
        logger.warning("Admin credentials not set in .env file!")
        return

    async for session in get_session():
        existing_admin = await UserRepository.get_user_by_email(session, admin_email)
        if not existing_admin:
            await UserRepository.create_user(
                session, email=admin_email, password=admin_password, is_admin=True
            )
            logger.info("Default admin user created!")
        else:
            logger.info("Admin user already exists")


@app.on_event("startup")
async def startup():
    await init_db()
    await create_default_admin()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", reload=True)
