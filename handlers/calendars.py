from datetime import datetime

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
)
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback

from data.db_manager import *
from .callbacks import sessions
from .forms import *
from .keyboards import *

# смс пользователей id - message
router = Router()


@router.callback_query(SimpleCalendarCallback.filter(), Form.waiting_date)
async def calendar_logic(
        callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext
):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback, callback_data)

    if selected:
        await state.update_data(selected_date=date.strftime("%d.%m.%Y"))
        await callback.message.answer(
            f"Выбрана дата: {date.strftime('%d.%m.%Y')}\n\n📝 Теперь отправьте ответ на домашнее задание.\n"
            f"Вы можете отправить текст, фото, документ.\nКогда закончите, нажмите кнопку 'Завершить'.",
            reply_markup=keyboard_save()
        )
        await state.set_state(Form.waiting_homework_answer)
    await callback.answer()


@router.callback_query(SimpleCalendarCallback.filter(), Form.waiting_get_hw_date)
async def calendar_get_hw_logic(
        callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext
):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback, callback_data)

    if selected:
        selected_date = date.strftime("%d.%m.%Y")
        homework = get_hw(selected_date)
        if homework:
            await callback.message.answer(f"Вот ответы на {selected_date}:\n\n")
            text = ""
            for h in homework:
                for answ in homework[h]:
                    text += f"Пользователь @{h} \nопубликовал ответ {answ['created_at'].strftime("%d.%m.%Y")} в {answ['created_at'].strftime("%H:%M")}\nпо предмету {answ['subject']}:\n"
                    if answ['text']:
                        text += f"{answ['text']}"
                    await callback.message.answer(text)
                    for doc in answ["files"]:
                        if doc["type"] == "photo":
                            caption_text = f"\nПодпись: {doc['caption']}" if doc['caption'] else ''
                            await callback.message.answer_photo(
                                doc["file_id"],
                                caption=f"Фото от @{h} по предмету {answ['subject']}.\n{caption_text}"
                            )
                        elif doc["type"] == "document":
                            caption_text = f"\nПодпись: {doc['caption']}" if doc['caption'] else ''
                            await callback.message.answer_document(
                                document=doc["file_id"],
                                caption=f"Документ от @{h} по предмету {answ['subject']}.\n{caption_text}",
                            )
                    text += "\n\n"
                    text = ""
        else:
            await callback.message.answer(f"Ответов на {selected_date} нет.")
        await state.clear()
        await callback.message.answer(
            "Выберите действие:", reply_markup=keyboard_after_get_hw()
        )
    await callback.answer()


@router.callback_query(SimpleCalendarCallback.filter(), Form.waiting_add_ht_date_student)
async def calendar_add_from_user(
        callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext
):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback, callback_data)

    if selected:
        selected_date = date.strftime("%d.%m.%Y")
        add_ht('qwerty', selected_date, "some_text", "some_text", "some_files", telegram_id=callback.from_user.id)

        await state.clear()
        await callback.message.answer(f'ДЗ добавлено на {selected_date}!')
        user = get_user_by_telegram_id(callback.from_user.id)
        user_name = user.username
        await send_notify_to_users(callback.bot, "boolean_notify_new_homework", 'Новое ДЗ!',
                                   f'Пользователь @{user_name}\nопубликовал ДЗ на {selected_date}!',
                                   except_user_id=callback.from_user.id
                                   )
        await callback.message.answer(
            "Выберите действие:", reply_markup=keyboard_after_get_hw()
        )
    await callback.answer()


@router.callback_query(SimpleCalendarCallback.filter(), Form.waiting_get_ht_date_netschool)
async def calendar_get_ht_netschool_logic(
        callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext
):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback, callback_data)

    if selected:
        try:
            selected_date = date.strftime("%d.%m.%Y")
            school = sessions[callback.message.from_user.id]
            hometask = "get_ht нужен в метод calendar_get_ht_netschool_logic"  # get_ht(selected_date)
            await callback.message.answer("ВНИМАНИЕ! Информация актуальна на 'во сколько'. База данных загружена 'кем-то'.")
            if hometask:
                await callback.message.answer(f"ДЗ на {selected_date}:\n\n")
                await callback.message.answer(f"{hometask}")
            else:
                await callback.message.answer(f"Дз с netschool на {selected_date} нет.")
            await state.clear()
            await callback.message.answer(
                "Выберите действие:", reply_markup=keyboard_after_get_ht()
            )
        except Exception as e:
            await callback.message.answer("ошибка на сторороне сервера попробуйте позже")
    await callback.answer()


@router.callback_query(SimpleCalendarCallback.filter(), Form.waiting_get_ht_date_student)
async def calendar_get_ht_student_logic(
        callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext
):
    calendar = SimpleCalendar()
    selected, date = await calendar.process_selection(callback, callback_data)

    if selected:
        selected_date = date.strftime("%d.%m.%Y")
        hometask = get_ht(selected_date, False)
        if hometask:
            text = f"ДЗ на {selected_date}:\n\n"
            for h in hometask:
                for answ in hometask[h]:
                    date_str_in_date = datetime.strptime(answ['created_at'].replace('T', ' '), "%Y-%m-%d %H:%M:%S")
                    text += f"Пользователь @{h} \nопубликовал задание {date_str_in_date.strftime("%d.%m.%Y")} в {date_str_in_date.strftime("%H:%M")}:\nпо предмету {answ['subject']}:\n\n"
                    if text:
                        text += f"{answ['description']}"
                    await callback.message.answer(text)
                    for doc in answ["files_json"]:
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
            await callback.message.answer(f"{hometask}")
        else:
            await callback.message.answer(f"ДЗ от пользователей на {selected_date} нет.")
        await state.clear()
        await callback.message.answer(
            "Выберите действие:", reply_markup=keyboard_after_get_ht_student()
        )
    await callback.answer()
