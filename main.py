import asyncio
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession

load_dotenv()

TOKEN = getenv("TOKEN")
PROXY_URL = getenv("PROXY_URL")

dp = Dispatcher()


@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    await message.answer("Hello! I'm a bot created with aiogram.")


# ЗАПУСК БОТА
async def main() -> None:
    session = AiohttpSession(proxy=PROXY_URL)
    bot = Bot(token=TOKEN, session=session)
    print("Бот запущен через прокси!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
