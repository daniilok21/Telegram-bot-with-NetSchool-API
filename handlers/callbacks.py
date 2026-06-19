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
from aiogram.utils.text_decorations import markdown_decoration
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from data.db_manager import *
from .keyboards import *
from .forms import *
from api.start import School
#смс пользователей id - message
sms_feature = {}
router = Router()


@router.callback_query(lambda c: c.data == "view_ht")
async def view_ht(callback: CallbackQuery):
    await callback.message.answer("Выберите:", reply_markup=keyboard_inline_view_ht())
    await callback.answer()


@router.callback_query(lambda c: c.data == "get_ht_netschool" or c.data == 'get_ht_date')
async def get_ht_netschool(callback: CallbackQuery, state: FSMContext):
    calendar = SimpleCalendar()
    await state.set_state(Form.waiting_get_ht_date_netschool)
    await callback.message.answer("📅 Выберите дату домашнего задания:", reply_markup= await calendar.start_calendar())
    await callback.answer()


@router.callback_query(lambda c: c.data == "get_ht_students" or c.data == 'get_ht_date_student')
async def get_ht_students(callback: CallbackQuery, state: FSMContext):
    calendar = SimpleCalendar()
    await state.set_state(Form.waiting_get_ht_date_student)
    await callback.message.answer("📅 Выберите дату домашнего задания:", reply_markup=await calendar.start_calendar())
    await callback.answer()


@router.callback_query(lambda c: c.data == "add_ht_student")
async def add_ht_student(callback: CallbackQuery, state: FSMContext):
    calendar = SimpleCalendar()
    await state.set_state(Form.waiting_add_ht_date_student)
    await callback.message.answer("📅 Выберите дату для добавления домашнего задания:", reply_markup=await calendar.start_calendar())
    await callback.answer()


@router.callback_query(lambda c: c.data == "add_answer_ht")
async def add_answer_ht(callback: CallbackQuery, state: FSMContext):
    calendar = SimpleCalendar()
    await state.set_state(Form.waiting_date)
    await callback.message.answer(
        "📅 Выберите дату домашнего задания:",
        reply_markup=await calendar.start_calendar(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "view_answer_ht")
async def view_answer_ht(callback: CallbackQuery):
    await callback.message.answer(
        "Выберите действие:", reply_markup=keyboard_inline_view_hw()
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "average_score")
async def average_score(callback: CallbackQuery):
    await callback.message.answer("ЗАГЛУШКА -  Средний балл")
    await callback.answer()


@router.callback_query(lambda c: c.data == "settings")
async def settings(callback: CallbackQuery):
    await callback.message.answer("Выберите:", reply_markup=keyboard_settings_menu())
    await callback.answer()


@router.callback_query(lambda c: c.data == "notify")
async def notify(callback: CallbackQuery):
    text = "🔔 Настройки уведомлений\n\nВыберите, о чем получать уведомления:\n\n"
    await callback.message.edit_text(text, reply_markup=keyboard_settings_notify(callback.from_user.id))
    await callback.answer()


@router.callback_query(lambda c: c.data == "toggle_notify_admins")
async def toggle_notify_admins(callback: CallbackQuery):
    current_setting = get_settings(callback.from_user.id, ["boolean_notify_admins"])
    add_settings(callback.from_user.id, "boolean_notify_admins", not current_setting['boolean_notify_admins'])
    await callback.message.edit_reply_markup(
        reply_markup=keyboard_settings_notify(callback.from_user.id)
    )


@router.callback_query(lambda c: c.data == "toggle_notify_new_answers")
async def toggle_notify_new_answers(callback: CallbackQuery):
    current_setting = get_settings(callback.from_user.id, ["boolean_notify_new_answers"])
    add_settings(callback.from_user.id, "boolean_notify_new_answers", not current_setting['boolean_notify_new_answers'])
    await callback.message.edit_reply_markup(
        reply_markup=keyboard_settings_notify(callback.from_user.id)
    )


@router.callback_query(lambda c: c.data == "toggle_notify_new_homework")
async def toggle_notify_new_homework(callback: CallbackQuery):
    current_setting = get_settings(callback.from_user.id, ["boolean_notify_new_homework"])
    add_settings(callback.from_user.id, "boolean_notify_new_homework", not current_setting['boolean_notify_new_homework'])
    await callback.message.edit_reply_markup(
        reply_markup=keyboard_settings_notify(callback.from_user.id)
    )

