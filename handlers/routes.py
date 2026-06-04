from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery
from pyexpat.errors import messages

from data.db_manager import *

router = Router()


class Form(StatesGroup):
    pass


def keyboard_inline_start():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📚 Посмотреть ДЗ", callback_data="view_ht"),
             InlineKeyboardButton(text="➕ Добавить ответ на ДЗ", callback_data="add_answer_ht")],
            [InlineKeyboardButton(text="📖 Посмотреть ответы на ДЗ", callback_data="view_answer_ht"),
             InlineKeyboardButton(text="📊 Средний балл", callback_data="average_score")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings"),
             InlineKeyboardButton(text="👤 Авторизоваться", callback_data="log_in")]
        ]
    )
    return keyboard


def keyboard_inline_view_hw():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📖 Все ответы за сегодня", callback_data="all_hw_today"),
             InlineKeyboardButton(text="🔍 Поиск по предмету", callback_data="get_hw_subj")],
        ]
    )
    return keyboard


@router.callback_query(lambda c: c.data == "all_hw_today")
async def all_hw_today(callback: CallbackQuery):
    homework = get_hw(datetime.now().strftime("%Y-%m-%d"))
    if not homework:
        await callback.message.answer("На сегодня ответов нет.")
        await callback.answer()
        return
    text = f'Ответы на сегодня: {homework}'



    await callback.message.answer(text)
    await callback.answer()


@router.callback_query(lambda c: c.data == "view_ht")
async def view_ht(callback: CallbackQuery):
    await callback.message.answer("ЗАГЛУШКА -  Посмотреть ДЗ")
    await callback.answer()


@router.callback_query(lambda c: c.data == "add_answer_ht")
async def add_answer_ht(callback: CallbackQuery):
    await callback.message.answer("Введите дату")
    await callback.answer()


@router.callback_query(lambda c: c.data == "view_answer_ht")
async def view_answer_ht(callback: CallbackQuery):
    await callback.message.answer('Выберите действие:', reply_markup=keyboard_inline_view_hw())
    await callback.answer()


@router.callback_query(lambda c: c.data == "average_score")
async def average_score(callback: CallbackQuery):
    await callback.message.answer("ЗАГЛУШКА -  Средний балл")
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings")
async def settings(callback: CallbackQuery):
    await callback.message.answer("ЗАГЛУШКА -  Настройки")
    await callback.answer()


@router.callback_query(lambda c: c.data == "log_in")
async def log_in(callback: CallbackQuery):
    await callback.message.answer("ЗАГЛУШКА -  Авторизоваться")
    await callback.answer()


@router.message(Command("start"))
async def start(message: Message):
    new_or_old_user_check_and_create(message.from_user.id)
    if check_user_is_allowed(message.from_user.id):
        await message.answer(
            "Привет! Я *бот*, _созданный_ с помощью aiogram.\n Пиши /help если нужна помощь",
            parse_mode="Markdown"
        )
        await message.answer('Выберите действие:', reply_markup=keyboard_inline_start())
    else:
        await message.answer('Вы не можете пользоваться ботом, попросите администраторов включить вас в белый список.')


@router.message(Command("help"))
@router.message(F.text.lower() == "помощь")
async def help(message: Message):
    await message.answer(
        "Команды:\n<b>/start</b> - начать работу с ботом\n<i>/help</i> - получить помощь<a href='https://google.com'>hello</a>\n/about - узнать о боте",
        parse_mode="HTML", reply_markup=keyboard_inline_start()
    )


@router.message(Command("about"))
async def about(message: Message):
    await message.answer(f"разработка бота. Твое имя {message.from_user.first_name}")


@router.message(Command("allow"))
async def allow(message: Message):
    if check_user_is_admin(message.from_user.id):
        command = message.text.strip().split()
        if len(command) == 2 and command[-1].isdigit():
            if give_user_allowed(command[-1]):
                await message.answer(f'Успешно, пользователь с telegram_id={command[-1]} добавлен в белый список!')
            else:
                await message.answer(f'Ошибка!')
        else:
            await message.answer("Некорректная команда! Пример: /allow 5126480415")
    else:
        await message.answer('У вас нет прав администратора для выполнения этой команды!')


@router.message(Command("deny"))
async def deny(message: Message):
    if check_user_is_admin(message.from_user.id):
        command = message.text.strip().split()
        if len(command) == 2 and command[-1].isdigit():
            if deny_user_allowed(command[-1]):
                await message.answer(
                    f'Успешно, пользователь с telegram_id={command[-1]} удален из белого списка!')
            else:
                await message.answer(f'Ошибка!')
        else:
            await message.answer("Некорректная команда! Пример: /deny 5126480415")
    else:
        await message.answer('У вас нет прав администратора для выполнения этой команды!')


@router.message(Command("users"))
async def users(message: Message):
    if check_user_is_admin(message.from_user.id):
        all_users = get_users()
        if not all_users:
            await message.answer('Список пользователей пуст!')
        else:
            text = ''
            for u in all_users:
                text += f'tg_id={u['telegram_id']} | is_allowed={u['is_allowed']} | is_admin={u['is_admin']}\n'
            await message.answer(text)
    else:
        await message.answer('У вас нет прав администратора для выполнения этой команды!')


@router.message()
async def talk(message: Message):
    await message.answer('Неизвестная команда!')
