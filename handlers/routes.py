from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from data.db_manager import *

router = Router()


def keyboard_user():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Расписание")],
            [KeyboardButton(text="Настройки"), KeyboardButton(text="Помощь")],
        ],
        resize_keyboard=True,
    )
    return keyboard

def keyboard_inline_user():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Сайт", url="https://net-school.cap.ru/")],
            [InlineKeyboardButton(text="Помощь", callback_data="help_callback")],
        ]
    )
    return keyboard


@router.message(Command("start"))
async def start(message: Message):
    await message.answer(
        "Привет! Я *бот*, _созданный_ с помощью aiogram.\n Пиши /help если нужна помощь",
        parse_mode="Markdown",
        reply_markup=keyboard_user()
    )
    await message.answer('Выберите действие:', reply_markup=keyboard_inline_user())


@router.message(Command("help"))
@router.message(F.text.lower() == "помощь")
async def help(message: Message):
    await message.answer(
        "Команды:\n<b>/start</b> - начать работу с ботом\n<i>/help</i> - получить помощь<a href='https://google.com'>hello</a>\n/about - узнать о боте",
        parse_mode="HTML", reply_markup=keyboard_inline_user()  
    )


@router.message(Command("about"))
async def about(message: Message):
    await message.answer(f"разработка бота. Твое имя {message.from_user.first_name}")


@router.message()
async def talk(message: Message):
    user = new_or_old_user_check_and_create(message.from_user.id)
    await message.answer(f"{chech_user_is_admin(message.from_user.id)}; your tg_id={type(message.from_user.id)}")