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
from api.service import School

# смс пользователей id - message
sms_feature = {}
router = Router()


@router.callback_query(F.data.startswith("subject_"))
async def homework_subject(callback: CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.split("_")[1])
    subjects = get_all_subjects()
    current_subject = get_subject_by_id(subject_id)
    current_state = await state.get_state()
    data = await state.get_data()
    if current_state == Form.waiting_hw_subject.state:
        await callback.message.answer(
            f"Выбранный предмет: {current_subject}\n\n"
            f"📝 Теперь отправьте ответ на домашнее задание.\n"
            f"Вы можете отправить текст, фото, документ.\nКогда закончите, нажмите кнопку 'Завершить'.",
            reply_markup=keyboard_save(),
        )
        await state.update_data(current_subject=current_subject)
        await state.set_state(Form.waiting_homework_answer)
    elif current_state == Form.waiting_ht_subject:
        await callback.message.answer(
            f"Выбранный предмет: {current_subject}\n\n"
            f"📝 Теперь отправьте домашнее задание.\n"
            f"Вы можете отправить текст, фото, документ.\nКогда закончите, нажмите кнопку 'Завершить'.",
            reply_markup=keyboard_save_ht(),
        )
        await state.update_data(current_subject=current_subject)
        await state.set_state(Form.waiting_hometask)
    elif current_state == Form.waiting_get_hw_date_by_subject2:
        selected_date = data.get("selected_date")
        homework = get_hw(selected_date, subject_name=current_subject)
        if homework:
            await callback.message.answer(
                f"Вот ответы на {selected_date} по предмету: {current_subject}\n\n"
            )
            text = ""
            for h in homework:
                for answ in homework[h]:
                    text += f"Пользователь @{h} \nопубликовал ответ {answ['created_at'].strftime('%d.%m.%Y')} в {answ['created_at'].strftime('%H:%M')}\nпо предмету {answ['subject']}:\n"
                    if answ["text"]:
                        text += f"{answ['text']}"
                    await callback.message.answer(text)
                    for doc in answ["files"]:
                        if doc["type"] == "photo":
                            caption_text = (
                                f"\nПодпись: {doc['caption']}" if doc["caption"] else ""
                            )
                            await callback.message.answer_photo(
                                doc["file_id"],
                                caption=f"Фото от @{h} по предмету {answ['subject']}.\n{caption_text}",
                            )
                        elif doc["type"] == "document":
                            caption_text = (
                                f"\nПодпись: {doc['caption']}" if doc["caption"] else ""
                            )
                            await callback.message.answer_document(
                                document=doc["file_id"],
                                caption=f"Документ от @{h} по предмету {answ['subject']}.\n{caption_text}",
                            )
                    text += "\n\n"
                    text = ""
        else:
            await callback.message.answer(
                f"Ответов на {selected_date} по предмету {current_subject} нет."
            )
        await state.clear()
        await callback.message.answer(
            "Выберите действие:", reply_markup=keyboard_after_get_hw()
        )
        await state.clear()
    elif current_state == Form.waiting_get_ht_date_by_subject2:
        selected_date = data.get("selected_date")
        hometask = get_ht(
            selected_date, isFromNetSchool=False, subject_name=current_subject
        )
        if hometask:
            text = f"ДЗ на {selected_date} по предмету {current_subject}:\n\n"
            for h in hometask:
                for answ in hometask[h]:
                    date_str_in_date = datetime.strptime(
                        answ["created_at"].replace("T", " "), "%Y-%m-%d %H:%M:%S"
                    )
                    text += f"Пользователь @{h} \nопубликовал задание {date_str_in_date.strftime('%d.%m.%Y')} в {date_str_in_date.strftime('%H:%M')}:\nпо предмету {answ['subject']}:\n\n"
                    if answ["description"]:
                        text += f"{answ['description']}"
                    await callback.message.answer(text)
                    for doc in answ["files"]:
                        if doc["type"] == "photo":
                            caption_text = (
                                f"\nПодпись: {doc['caption']}" if doc["caption"] else ""
                            )
                            await callback.message.answer_photo(
                                doc["file_id"],
                                caption=f"Фото от @{h} по предмету {answ['subject']}.\n{caption_text}",
                            )
                        elif doc["type"] == "document":
                            caption_text = (
                                f"\nПодпись: {doc['caption']}" if doc["caption"] else ""
                            )
                            await callback.message.answer_document(
                                document=doc["file_id"],
                                caption=f"Документ от @{h} по предмету {answ['subject']}.\n{caption_text}",
                            )
                    text += "\n\n"
                    text = ""
        else:
            await callback.message.answer(
                f"ДЗ от пользователей на {selected_date} по предмету {current_subject} нет."
            )
        await state.clear()
        await callback.message.answer(
            "Выберите действие:", reply_markup=keyboard_after_get_ht_student()
        )

    await callback.answer()


@router.message(Form.waiting_homework_answer, F.photo | F.document | F.text)
async def homework_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    selected_date = data.get("selected_date")
    text = data.get("answer", "")
    files = data.get("files", [])
    if message.text:
        text += message.text + "\n"
        await message.answer(f"📝 Текст добавлен!")
    elif message.photo:
        file_id = message.photo[-1].file_id
        files.append(
            {
                "file_id": file_id,
                "type": "photo",
                "caption": message.caption if message.caption else None,
            }
        )
        await message.answer(f"📸 Фото добавлено! Всего файлов: {len(files)}")
    elif message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        if not file_name:
            file_name = "Document"
        files.append(
            {
                "file_id": file_id,
                "type": "document",
                "name": file_name,
                "caption": message.caption if message.caption else None,
            }
        )
        await message.answer(
            f"Документ '{file_name}' добавлен! Всего файлов: {len(files)}"
        )
    else:
        await message.answer(
            "❌ Неподдерживаемый тип файла. Отправьте текст, фото или документ."
        )
    await state.update_data(answer=text)
    await state.update_data(files=files)


@router.callback_query(lambda c: c.data == "get_hw_subject")
async def get_hw_subject(callback: CallbackQuery, state: FSMContext):
    calendar = SimpleCalendar()
    await state.set_state(Form.waiting_get_hw_date_by_subject)
    await callback.message.answer(
        "📅 Выберите дату домашнего задания:",
        reply_markup=await calendar.start_calendar(),
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "get_ht_subject")
async def get_ht_subject(callback: CallbackQuery, state: FSMContext):
    calendar = SimpleCalendar()
    await state.set_state(Form.waiting_get_ht_date_by_subject)
    await callback.message.answer(
        "📅 Выберите дату домашнего задания:",
        reply_markup=await calendar.start_calendar(),
    )
    await callback.answer()


@router.message(Form.waiting_hometask, F.photo | F.document | F.text)
async def hometask_text(message: Message, state: FSMContext):
    data = await state.get_data()
    selected_date = data.get("selected_date")
    text = data.get("answer", "")
    files = data.get("files", [])
    if message.text:
        text += message.text + "\n"
        await message.answer(f"📝 Текст добавлен!")
    elif message.photo:
        file_id = message.photo[-1].file_id
        files.append(
            {
                "file_id": file_id,
                "type": "photo",
                "caption": message.caption if message.caption else None,
            }
        )
        await message.answer(f"📸 Фото добавлено! Всего файлов: {len(files)}")
    elif message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        if not file_name:
            file_name = "Document"
        files.append(
            {
                "file_id": file_id,
                "type": "document",
                "name": file_name,
                "caption": message.caption if message.caption else None,
            }
        )
        await message.answer(
            f"Документ '{file_name}' добавлен! Всего файлов: {len(files)}"
        )
    else:
        await message.answer(
            "❌ Неподдерживаемый тип файла. Отправьте текст, фото или документ."
        )
    await state.update_data(answer=text)
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
    subject = data.get("current_subject", "?")
    if date:
        if files or text:
            if add_hw(callback.from_user.id, subject, date, text, files):
                await callback.message.answer(f"Ответ сохранен на дату\n{date}")
                user = get_user_by_telegram_id(callback.from_user.id)
                user_name = user.username
                await send_notify_to_users(
                    callback.bot,
                    "boolean_notify_new_answers",
                    "Новый ответ на ДЗ!",
                    f"Пользователь @{user_name}\nопубликовал ответ на ДЗ по предмету {subject} на {date}!",
                    except_user_id=callback.from_user.id,
                )
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


@router.callback_query(lambda c: c.data == "save_ht")
async def save_ht(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    date = data.get("selected_date")
    text = data.get("answer")
    files = data.get("files")
    subject = data.get("current_subject", "?")
    if date:
        if files or text:
            if add_ht(
                subject,
                date,
                description=text,
                files=files,
                telegram_id=callback.from_user.id,
            ):
                await callback.message.answer(f"Задание сохранено на дату\n{date}")
                user = get_user_by_telegram_id(callback.from_user.id)
                user_name = user.username
                await send_notify_to_users(
                    callback.bot,
                    "boolean_notify_new_homework",
                    "Новое ДЗ!",
                    f"Пользователь @{user_name}\nопубликовал ДЗ по предмету {subject} на {date}!",
                    except_user_id=callback.from_user.id,
                )
            else:
                await callback.message.answer(f"Ошибка!")
        else:
            await callback.message.answer("Ошибка! Нельзя сохранять пустое задание!")
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
            text += f"Пользователь @{h} \nопубликовал ответ {answ['created_at'].strftime('%d.%m.%Y')} в {answ['created_at'].strftime('%H:%M')}:\nпо предмету {answ['subject']}: \n\n"
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
