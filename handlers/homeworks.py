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
sms_feature = {}
router = Router()
sessions = {}


@router.message(Form.waiting_homework_answer)
async def homework_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    selected_date = data.get("selected_date")
    answer = message.text
    if answer != "/skip":
        await state.update_data(selected_date=selected_date, answer=answer, files=[])
    await message.answer(
        f"Добавьте файлы. Когда закончите, нажмите кнопку 'Завершить'.",
        reply_markup=keyboard_save(),
    )
    await state.set_state(Form.waiting_files)


@router.message(Form.waiting_files, F.photo | F.document)
async def get_files(message: Message, state: FSMContext):
    data = await state.get_data()
    files = data.get("files", [])
    if message.photo:
        file_id = message.photo[-1].file_id
        files.append({"file_id": file_id, "type": "photo"})
        await message.answer(f"📸 Фото добавлено! Всего: {len(files)}")
    elif message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        if not file_name:
            file_name = "Document"
        files.append({"file_id": file_id, "type": "document", "name": file_name})
        await message.answer(f"Документ '{file_name}' добавлен! Всего: {len(files)}")

    await state.update_data(files=files)


@router.callback_query(lambda c: c.data == "back")
async def back(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Выберите действие:", reply_markup=keyboard_inline_start()
    )
    await state.clear()


@router.callback_query(lambda c: c.data == "save_hw")
async def save_hw(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    date = data.get("selected_date")
    text = data.get("answer")
    files = data.get("files")
    if date:
        if files or text:
            if add_hw(callback.from_user.id, "qwerty", date, text, files):
                await callback.message.answer(f"Ответ сохранен на дату\n{date}")
            else:
                await callback.message.answer(f"Ошибка!")
        else:
            await callback.message.answer("Ошибка! Нельзя сохранять пустой ответ!")
    else:
        await callback.message.answer("Ошибка!")
    await callback.message.answer(
        "Выберите действие:", reply_markup=keyboard_inline_start()
    )
    await callback.answer()
    await state.clear()


@router.callback_query(lambda c: c.data == "get_hw_date")
async def get_hw_date(callback: CallbackQuery, state: FSMContext):
    calendar = SimpleCalendar()
    await state.set_state(Form.waiting_get_hw_date)
    await callback.message.answer(
        "📅 Выберите дату для просмотра домашних заданий:",
        reply_markup=await calendar.start_calendar(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "all_hw_tomorrow")
async def all_hw_tomorrow(callback: CallbackQuery):
    homework = get_hw((datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y"))
    if not homework:
        await callback.message.answer("На завтра ответов нет.")
        await callback.answer()
        return
    text = f"Ответы на завтра:\n\n"
    for h in homework:
        for answ in homework[h]:
            text += f"Пользователь @{h} \nопубликовал ответ {answ['created_at'].strftime("%d.%m.%Y")} в {answ['created_at'].strftime("%H:%M")}:\nпо предмету {answ['subject']}: \n\n"
            if text:
                text += f"{answ['text']}"
            await callback.message.answer(text)
            for doc in answ["files"]:
                if doc["type"] == "photo":
                    await callback.message.answer_photo(
                        doc["file_id"],
                        caption=f"Фото от @{h} по предмету: {answ['subject']}",
                    )
                elif doc["type"] == "document":
                    await callback.message.answer_document(
                        document=doc["file_id"],
                        caption=f"Документ от @{h} по предмету {answ['subject']}:\n",
                    )
            text += "\n\n"
            text = ""
    await callback.message.answer(
        "Выберите действие:", reply_markup=keyboard_inline_start()
    )
    await callback.answer()