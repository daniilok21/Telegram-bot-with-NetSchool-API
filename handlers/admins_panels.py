from calendar import calendar
from datetime import timedelta, datetime
from importlib.resources import files
import asyncio
from logging import fatal

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardRemove,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from data.db_manager import *
from .keyboards import *
from .forms import *
from api.start import School
#смс пользователей id - message
router = Router()

@router.message(Command("allow"))
async def allow(message: Message):
    if check_user_is_admin(message.from_user.id):
        command = message.text.strip().split()
        if len(command) == 2 and command[-1].isdigit():
            if give_user_allowed(command[-1]):
                await message.answer(
                    f"Успешно, пользователь с telegram_id={command[-1]} добавлен в белый список!"
                )
            else:
                await message.answer(f"Ошибка!")
        else:
            await message.answer("Некорректная команда! Пример: /allow 5126480415")
    else:
        await message.answer(
            "У вас нет прав администратора для выполнения этой команды!"
        )


@router.message(Command("deny"))
async def deny(message: Message):
    if check_user_is_admin(message.from_user.id):
        command = message.text.strip().split()
        if len(command) == 2 and command[-1].isdigit():
            if deny_user_allowed(command[-1]):
                await message.answer(
                    f"Успешно, пользователь с telegram_id={command[-1]} удален из белого списка!"
                )
            else:
                await message.answer(f"Ошибка!")
        else:
            await message.answer("Некорректная команда! Пример: /deny 5126480415")
    else:
        await message.answer(
            "У вас нет прав администратора для выполнения этой команды!"
        )


@router.message(Command("users"))
async def users(message: Message):
    if check_user_is_admin(message.from_user.id):
        all_users = get_users()
        if not all_users:
            await message.answer("Список пользователей пуст!")
        else:
            text = ""
            for u in all_users:
                text += f"tg_id={u['telegram_id']} | is_allowed={u['is_allowed']} | is_admin={u['is_admin']}\n"
            await message.answer(text)
    else:
        await message.answer(
            "У вас нет прав администратора для выполнения этой команды!"
        )


@router.message(Command("say"))
async def say(message: Message):
    command = message.text.replace('/say', '')
    if check_user_is_admin(message.from_user.id):
        if command:
            user = get_user_by_telegram_id(message.from_user.id)
            await send_notify_to_users(message.bot, "boolean_notify_admins", 'Объявление!',
                                       f'@{user.username}: {command}',
                                       except_user_id=message.from_user.id
                                       )
        else:
            await message.answer('Нельзя отправить пустой текст!')
    else:
        await message.answer(
            "У вас нет прав администратора для выполнения этой команды!"
        )