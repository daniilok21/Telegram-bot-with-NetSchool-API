import asyncio
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession

from data import db_session
from data.users import User

load_dotenv()

TOKEN = getenv("TOKEN")
PROXY_URL = getenv("PROXY_URL")

dp = Dispatcher()


def new_or_old_user_check_and_create(telegram_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()
    print(user)
    db_sess.close()


@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    telegram_id = message.from_user.id
    new_or_old_user_check_and_create(telegram_id)
    await message.answer("Hello! I'm a bot created with aiogram.")



# ЗАПУСК БОТА
async def main() -> None:
    session = AiohttpSession(proxy=PROXY_URL)
    bot = Bot(token=TOKEN, session=session)
    print("Бот запущен!")

    await dp.start_polling(bot)


if __name__ == "__main__":
    db_session.global_init("db/database.db")
    asyncio.run(main())
