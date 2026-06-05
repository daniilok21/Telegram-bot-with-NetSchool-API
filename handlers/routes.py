from datetime import timedelta
from importlib.resources import files

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    CallbackQuery, ReplyKeyboardRemove
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram_calendar import SimpleCalendar, SimpleCalendarCallback
from data.db_manager import *

router = Router()


class Form(StatesGroup):
    waiting_date = State()
    waiting_homework_answer = State()
    waiting_files = State()
    waiting_text = State()
    selected_date = State()
    answer = State()
    waiting_get_hw_date = State()


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
            [InlineKeyboardButton(text="📖 Все ответы на завтра", callback_data="all_hw_tomorrow"),
             InlineKeyboardButton(text="🔍 Поиск по дате", callback_data="get_hw_date")],
        ]
    )
    return keyboard


def keyboard_save():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Завершить", callback_data="save_hw")]
        ]
    )
    return keyboard


def keyboard_reply_help():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='Помощь')]
        ],
        resize_keyboard=True
    )
    return keyboard


def keyboard_after_get_hw():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data='back'),
             InlineKeyboardButton(text="🔍 Поиск по дате", callback_data="get_hw_date")],
        ]
    )
    return keyboard


@router.callback_query(SimpleCalendarCallback.filter(), Form.waiting_date)
async def calendar_logic(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    calendar = SimpleCalendar(locale='RU')
    selected, date = await calendar.process_selection(callback, callback_data)

    if selected:
        await state.update_data(selected_date=date.strftime("%d.%m.%Y"))
        await callback.message.answer(
            f"Выбрана дата: {date.strftime('%d.%m.%Y')}\n\nТеперь напишите текст ответа на домашнее задание. Вы сможете выбрать файлы позже.\nЕсли не хотите добавлять текст напишите /skip"
        )
        await state.set_state(Form.waiting_homework_answer)
    await callback.answer()


@router.callback_query(SimpleCalendarCallback.filter(), Form.waiting_get_hw_date)
async def calendar_get_hw_logic(callback: CallbackQuery, callback_data: SimpleCalendarCallback, state: FSMContext):
    calendar = SimpleCalendar(locale='RU')
    selected, date = await calendar.process_selection(callback, callback_data)

    if selected:
        selected_date = date.strftime("%d.%m.%Y")
        homework = get_hw(selected_date)
        if homework:
            await callback.message.answer(
                f"Вот ответы на {selected_date}:\n\n"
            )
            text = ''
            for h in homework:
                for answ in homework[h]:
                    text += f"Пользователь @{h} \nопубликовал ответ {answ['created_at'].strftime("%d.%m.%Y")} в {answ['created_at'].strftime("%H:%M")}:\nпо предмету: {answ['subject']}:"
                    if text:
                        text += f"{answ['text']}"
                    await callback.message.answer(text)
                    for doc in answ['files']:
                        if doc['type'] == 'photo':
                            await callback.message.answer_photo(doc['file_id'],
                                                                caption=f"Фото от @{h} по предмету: {answ['subject']}")
                        elif doc['type'] == 'document':
                            await callback.message.answer_document(document=doc['file_id'],
                                                                   caption=f"Документ от @{h} по предмету {answ['subject']}:\n")
                    text += '\n\n'
                    text = ''
        else:
            await callback.message.answer(f'Ответов на {selected_date} нет.')
    await state.clear()
    await callback.message.answer('Выберите действие:', reply_markup=keyboard_after_get_hw())
    await callback.answer()


@router.message(Form.waiting_homework_answer)
async def homework_answer(message: Message, state: FSMContext):
    data = await state.get_data()
    selected_date = data.get("selected_date")
    answer = message.text
    if answer != '/skip':
        await state.update_data(selected_date=selected_date, answer=answer, files=[])
    await message.answer(f"Добавьте файлы. Когда закончите, нажмите кнопку 'Завершить'.", reply_markup=keyboard_save())
    await state.set_state(Form.waiting_files)



@router.message(Form.waiting_files, F.photo | F.document)
async def get_files(message: Message, state: FSMContext):
    data = await state.get_data()
    files = data.get('files', [])
    if message.photo:
        file_id = message.photo[-1].file_id
        files.append({"file_id": file_id, "type": "photo"})
        await message.answer(f"📸 Фото добавлено! Всего: {len(files)}")
    elif message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        if not file_name:
            file_name = 'Document'
        files.append({"file_id": file_id, "type": "document", "name": file_name})
        await message.answer(f"Документ '{file_name}' добавлен! Всего: {len(files)}")

    await state.update_data(files=files)


@router.callback_query(lambda c: c.data == "back")
async def back(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer('Выберите действие:', reply_markup=keyboard_inline_start())
    await state.clear()


@router.callback_query(lambda c: c.data == "save_hw")
async def save_hw(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    date = data.get("selected_date")
    text = data.get('answer')
    files = data.get('files')
    print()
    if date:
        if files or text:
            if add_hw(callback.from_user.id, 'qwerty', date, text, files):
                await callback.message.answer(f'Ответ сохранен на дату\n{date}')
            else:
                await callback.message.answer(f'Ошибка!')
        else:
            await callback.message.answer("Ошибка! Нельзя сохранять пустой ответ!")
    else:
        await callback.message.answer('Ошибка!')
    await callback.message.answer('Выберите действие:', reply_markup=keyboard_inline_start())
    await callback.answer()
    await state.clear()


@router.callback_query(lambda c: c.data == "get_hw_date")
async def get_hw_date(callback: CallbackQuery, state: FSMContext):
    calendar = SimpleCalendar(locale='ru_RU')
    await state.set_state(Form.waiting_get_hw_date)
    await callback.message.answer(
        "📅 Выберите дату для просмотра домашних заданий:",
        reply_markup=await calendar.start_calendar()
    )
    await callback.answer()

@router.callback_query(lambda c: c.data == "all_hw_tomorrow")
async def all_hw_tomorrow(callback: CallbackQuery):
    homework = get_hw((datetime.now() + timedelta(days=1)).strftime("%d.%m.%Y"))
    if not homework:
        await callback.message.answer("На завтра ответов нет.")
        await callback.answer()
        return
    text = f'Ответы на завтра:\n\n'
    for h in homework:
        for answ in homework[h]:
            text += f"Пользователь @{h} \nопубликовал ответ {answ['created_at'].strftime("%d.%m.%Y")} в {answ['created_at'].strftime("%H:%M")}:\nпо предмету {answ['subject']}:"
            if text:
                text += f"{answ['text']}"
            await callback.message.answer(text)
            for doc in answ['files']:
                if doc['type'] == 'photo':
                    await callback.message.answer_photo(doc['file_id'], caption=f"Фото от @{h} по предмету: {answ['subject']}")
                elif doc['type'] == 'document':
                    await callback.message.answer_document(document=doc['file_id'], caption=f"Документ от @{h} по предмету {answ['subject']}:\n")
            text += '\n\n'
            text = ''
    await callback.message.answer('Выберите действие:', reply_markup=keyboard_inline_start())
    await callback.answer()


@router.callback_query(lambda c: c.data == "view_ht")
async def view_ht(callback: CallbackQuery):
    await callback.message.answer("ЗАГЛУШКА -  Посмотреть ДЗ")
    await callback.answer()


@router.callback_query(lambda c: c.data == "add_answer_ht")
async def add_answer_ht(callback: CallbackQuery, state: FSMContext):
    calendar = SimpleCalendar(locale='ru_RU')
    await state.set_state(Form.waiting_date)
    await callback.message.answer("📅 Выберите дату домашнего задания:", reply_markup=await calendar.start_calendar())
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
    new_or_old_user_check_and_create(message.from_user.id, message.from_user.username)
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
        parse_mode="HTML",reply_markup=ReplyKeyboardRemove()
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
    await message.answer('Неизвестная команда!', reply_markup=keyboard_reply_help())
