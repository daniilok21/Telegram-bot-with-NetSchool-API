from calendar import calendar
from datetime import timedelta, datetime
from importlib.resources import files
import asyncio
from logging import fatal
from .routes import sessions, add_user_message, delete_last_n_messages
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

@router.callback_query(SimpleCalendarCallback.filter(), Form.waiting_date)
async def calendar_logic(
    callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext
):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback, callback_data)
    if callback_data.act == "CANCEL":
        await state.clear()
        await delete_last_n_messages(callback.from_user.id, callback.bot, 2)
        msg = await callback.message.answer(
            "Выберите действие:", reply_markup=keyboard_inline_start()
        )
        await add_user_message(callback.from_user.id, msg.message_id)
    if selected:
        selected_date = date.strftime('%d.%m.%Y')
        msg = await callback.message.answer(
            f"Выбрана дата: {selected_date}\n\n📖Теперь введите название предмета:\n",
            reply_markup=keyboard_inline_subjects()
        )
        await add_user_message(callback.from_user.id, msg.message_id)
        await state.update_data(selected_date=selected_date)
        await state.set_state(Form.waiting_hw_subject)


    await callback.answer()


@router.callback_query(SimpleCalendarCallback.filter(), Form.waiting_get_hw_date)
async def calendar_get_hw_logic(
    callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext
):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback, callback_data)

    if callback_data.act == "CANCEL":
        await state.clear()
        await delete_last_n_messages(callback.from_user.id, callback.bot, 2)
        msg = await callback.message.answer(
            "Выберите действие:", reply_markup=keyboard_inline_view_hw()
        )
        await add_user_message(callback.from_user.id, msg.message_id)
    if selected:
        msgs = []
        selected_date = date.strftime("%d.%m.%Y")
        homework = get_hw(selected_date)
        if homework:
            msgs.append(await callback.message.answer(f"Вот ответы на {selected_date}:\n\n"))
            text = ""
            for h in homework:
                for answ in homework[h]:
                    text += f"Пользователь @{h} \nопубликовал ответ {answ['created_at'].strftime("%d.%m.%Y")} в {answ['created_at'].strftime("%H:%M")}\nпо предмету {answ['subject']}:\n"
                    if answ['text']:
                        text += f"{answ['text']}"
                    msgs.append(await callback.message.answer(text))
                    for doc in answ["files"]:
                        if doc["type"] == "photo":
                            caption_text = f"\nПодпись: {doc['caption']}" if doc['caption'] else ''
                            msgs.append(await callback.message.answer_photo(
                                doc["file_id"],
                                caption=f"Фото от @{h} по предмету {answ['subject']}.\n{caption_text}"
                            ))
                        elif doc["type"] == "document":
                            caption_text = f"\nПодпись: {doc['caption']}" if doc['caption'] else ''
                            msgs.append(await callback.message.answer_document(
                                document=doc["file_id"],
                                caption=f"Документ от @{h} по предмету {answ['subject']}.\n{caption_text}",
                            ))
                    text += "\n\n"
                    text = ""
        else:
            msgs.append(await callback.message.answer(f"Ответов на {selected_date} нет."))
        await state.clear()
        msgs.append(await callback.message.answer(
            "Выберите действие:", reply_markup=keyboard_after_get_hw()
        ))

        for msg in msgs:
            await add_user_message(callback.from_user.id, msg.message_id)

    await callback.answer()


@router.callback_query(SimpleCalendarCallback.filter(), Form.waiting_get_hw_date_by_subject)
async def calendar_get_hw_date_by_subject(
    callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext
):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback, callback_data)

    if callback_data.act == "CANCEL":
        await state.clear()
        await delete_last_n_messages(callback.from_user.id, callback.bot, 2)
        msg = await callback.message.answer(
            "Выберите действие:", reply_markup=keyboard_inline_view_hw()
        )
        await add_user_message(callback.from_user.id, msg.message_id)
    if selected:
        msg = await callback.message.answer("Выберите предмет:", reply_markup=keyboard_inline_subjects())
        await state.set_state(Form.waiting_get_hw_date_by_subject2)
        await state.update_data(selected_date=date.strftime("%d.%m.%Y"))
        await add_user_message(callback.from_user.id, msg.message_id)

    await callback.answer()


@router.callback_query(SimpleCalendarCallback.filter(), Form.waiting_get_ht_date_by_subject)
async def calendar_get_ht_date_by_subject(
    callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext
):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback, callback_data)

    if callback_data.act == "CANCEL":
        await state.clear()
        await delete_last_n_messages(callback.from_user.id, callback.bot, 2)
        msg = await callback.message.answer(
            "Выберите действие:", reply_markup=keyboard_inline_view_ht()
        )
        await add_user_message(callback.from_user.id, msg.message_id)
    if selected:
        msg = await callback.message.answer("Выберите предмет:", reply_markup=keyboard_inline_subjects())
        await state.set_state(Form.waiting_get_ht_date_by_subject2)
        await state.update_data(selected_date=date.strftime("%d.%m.%Y"))
        await add_user_message(callback.from_user.id, msg.message_id)

    await callback.answer()


@router.callback_query(SimpleCalendarCallback.filter(), Form.waiting_add_ht_date_student)
async def calendar_add_from_user(
    callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext
):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback, callback_data)

    if callback_data.act == "CANCEL":
        await state.clear()
        await delete_last_n_messages(callback.from_user.id, callback.bot, 2)
        msg = await callback.message.answer(
            "Выберите действие:", reply_markup=keyboard_inline_start()
        )
        await add_user_message(callback.from_user.id, msg.message_id)
    if selected:
        selected_date = date.strftime('%d.%m.%Y')
        msg = await callback.message.answer(
            f"Выбрана дата: {selected_date}\n\n📖Теперь введите название предмета:\n",
            reply_markup=keyboard_inline_subjects()
        )
        await add_user_message(callback.from_user.id, msg.message_id)
        await state.update_data(selected_date=selected_date)
        await state.set_state(Form.waiting_ht_subject)
    await callback.answer()


@router.callback_query(SimpleCalendarCallback.filter(), Form.waiting_get_ht_date_netschool)
async def calendar_get_ht_netschool_logic(
    callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext
):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback, callback_data)

    if callback_data.act == "CANCEL":
        await state.clear()
        await delete_last_n_messages(callback.from_user.id, callback.bot, 2)
        msg = await callback.message.answer(
            "Выберите действие:", reply_markup=keyboard_inline_view_ht()
        )
        await add_user_message(callback.from_user.id, msg.message_id)
    if selected:
        msgs = []
        try:
            selected_date = date.strftime("%d.%m.%Y")
            school = sessions.get(callback.from_user.id)
            msgs.append(await callback.message.answer(await school.today_homework(str(date.strftime("%Y, %-m, %-d")))))
            await state.clear()
            msgs.append(await callback.message.answer(
                "Выберите действие:", reply_markup=keyboard_after_get_ht()
            ))
        except Exception as e:
            school = sessions.get(callback.from_user.id)
            msgs.append(await callback.message.answer(f"ошибка на сторороне сервера попробуйте позже\nошибка {e}"))

        for msg in msgs:
            await add_user_message(callback.from_user.id, msg.message_id)

    await callback.answer()


@router.callback_query(SimpleCalendarCallback.filter(), Form.waiting_get_ht_date_student)
async def calendar_get_ht_student_logic(
    callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext
):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback, callback_data)

    if callback_data.act == "CANCEL":
        await state.clear()
        await delete_last_n_messages(callback.from_user.id, callback.bot, 2)
        msg = await callback.message.answer(
            "Выберите действие:", reply_markup=keyboard_inline_view_ht()
        )
        await add_user_message(callback.from_user.id, msg.message_id)
    if selected:
        msgs = []
        selected_date = date.strftime("%d.%m.%Y")
        hometask = get_ht(selected_date, False)
        if hometask:
            text = f"ДЗ на {selected_date}:\n\n"
            for h in hometask:
                for answ in hometask[h]:
                    created_at = answ['created_at'].replace('T', ' ').split('.')[0]
                    date_str_in_date = datetime.strptime(created_at, "%Y-%m-%d %H:%M:%S")
                    text += f"Пользователь @{h} \nопубликовал задание {date_str_in_date.strftime("%d.%m.%Y")} в {date_str_in_date.strftime("%H:%M")}:\nпо предмету {answ['subject']}:\n\n"
                    if answ['description']:
                        text += f"{answ['description']}"
                    msgs.append(await callback.message.answer(text))
                    for doc in answ["files"]:
                        if doc["type"] == "photo":
                            caption_text = f"\nПодпись: {doc['caption']}" if doc['caption'] else ''
                            msgs.append(await callback.message.answer_photo(
                                doc["file_id"],
                                caption=f"Фото от @{h} по предмету {answ['subject']}.\n{caption_text}"
                            ))
                        elif doc["type"] == "document":
                            caption_text = f"\nПодпись: {doc['caption']}" if doc['caption'] else ''
                            msgs.append(await callback.message.answer_document(
                                document=doc["file_id"],
                                caption=f"Документ от @{h} по предмету {answ['subject']}.\n{caption_text}",
                            ))
                    text += "\n\n"
                    text = ""
        else:
            msgs.append(await callback.message.answer(f"ДЗ от пользователей на {selected_date} нет."))
        await state.clear()
        msgs.append(await callback.message.answer(
            "Выберите действие:", reply_markup=keyboard_after_get_ht_student()
        ))

        for msg in msgs:
            await add_user_message(callback.from_user.id, msg.message_id)

    await callback.answer()