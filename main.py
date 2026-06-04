import asyncio
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession


from data import db_session
from data.users import User


from handlers.routes import router

load_dotenv()

TOKEN = getenv("TOKEN")
PROXY_URL = getenv("PROXY_URL")

dp = Dispatcher()
dp.include_router(router)

# ЗАПУСК БОТА
async def main() -> None:
    try:
        session = AiohttpSession(proxy=PROXY_URL)
        bot = Bot(token=TOKEN, session=session)
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