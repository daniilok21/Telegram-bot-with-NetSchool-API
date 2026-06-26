from calendar import calendar

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

load_dotenv()
import asyncio
from os import getenv


from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession

from data import db_session
from data.users import User
from data.db_manager import init_subjects

from handlers.routes import router
from handlers.calendars import router as calendar_router
from handlers.homeworks import router as homeworks_router
from handlers.admins_panels import router as admins_router
from handlers.callbacks import router as callback_router


TOKEN = getenv("TOKEN")
PROXY_URL = getenv("PROXY_URL")

dp = Dispatcher()
dp.include_router(calendar_router)
dp.include_router(homeworks_router)
dp.include_router(admins_router)
dp.include_router(callback_router)
dp.include_router(router)


subjects = [
    "Биология",
    "Биология профиль/биол проф",
    "Вероятность и статистика",
    "География",
    "Геометрия",
    "Ин.яз./Английский язык",
    "Индивидуальный проект",
    "Информатика",
    "Информатика профиль/инф проф",
    "История",
    "История профиль/ист проф",
    "Литература",
    "Математика профиль/Профиль матем",
    "Обществознание",
    "Обществознание профиль/Общ.проф",
    "Основы безопасности и защиты Родины",
    "Родная литература (чувашская)",
    "Русский язык",
    "Физика",
    "Физика профиль/физика пр",
    "Физкультура/Ж",
    "Физкультура/М",
    "Химия",
    "химия профиль/химия проф",
]


# ЗАПУСК БОТА
async def main() -> None:
    try:
        session = AiohttpSession(proxy=PROXY_URL)
        bot = Bot(token=TOKEN, session=session)
        init_subjects(subjects)
        print("Бот запускается...")

        await dp.start_polling(bot)
    except Exception as e:
        print(f"Ошибка в запуске бота!: {e}")
        try:
            bot = Bot(token=TOKEN)
            print("Бот запускается без прокси...")
            await dp.start_polling(bot)
        except Exception as e:
            print(f"Ошибка в запуске бота без прокси!: {e}")


if __name__ == "__main__":
    db_session.global_init("db/database.db")
    asyncio.run(main())
