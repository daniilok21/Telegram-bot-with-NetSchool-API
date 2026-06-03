from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

router = Router()


def keyboard_user():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🗓️Сегодня"),
                KeyboardButton(text="🗓️Завтра"),
                KeyboardButton(text="🗓️Неделя"),
            ],
            [
                KeyboardButton(text="🔍Поиск"),
                KeyboardButton(text="⭐Избранное"),
                KeyboardButton(text="📊Статистика"),
            ],
        ],
        resize_keyboard=True,
    )
    return keyboard


def keyboard_inline_user():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📚ДЗ на сегодня", callback_data="today_homework_callback"
                )
            ],
            [InlineKeyboardButton(text="📚ДЗ на завтра", callback_data="tomorrow_homework_callback")],
            [InlineKeyboardButton(text="📅Выбрать дату", callback_data="select_date_callback")],
            [
                InlineKeyboardButton(
                    text="📝Мои дополнения", callback_data="my_additions_callback"
                )
            ],
            [InlineKeyboardButton(text="⚙️Настройки", callback_data="settings_callback")],
        ]
    )
    return keyboard


@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "👋 Привет! 📅 Я твой бот для удобного доступа к расписанию из NetSchool 📚✨.",
        reply_markup=keyboard_user(),
    )
    await message.answer("Выберите действие:", reply_markup=keyboard_inline_user())


@router.callback_query(F.data == "today_homework_callback")
async def today_homework(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Вы выбрали ДЗ на сегодня!")


@router.callback_query(F.data == "tomorrow_homework_callback")
async def tomorrow_homework(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Вы выбрали ДЗ на завтра!")


@router.callback_query(F.data == "select_date_callback")
async def select_date(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Выберите дату")


@router.callback_query(F.data == "my_additions_callback")
async def additionals(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Дополенения")


@router.callback_query(F.data == "settings_callback")
async def settings(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer("Вы выбрали Настройки!")


# @router.message(Command("help"))
# @router.message(F.text.lower() == "помощь")
# async def help(message: Message):
#     await message.answer(
#         "Команды:\n<b>/start</b> - начать работу с ботом\n<i>/help</i> - получить помощь<a href='https://google.com'>hello</a>\n/about - узнать о боте",
#         parse_mode="HTML", reply_markup=keyboard_inline_user()
#     )


# @router.message(Command("about"))
# async def about(message: Message):
#     await message.answer(f"разработка бота. Твое имя {message.from_user.first_name}")
