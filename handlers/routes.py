import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
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


@router.message(Command("start"))
async def start(message: Message):
    school = School(login="", password="", user_id=message.from_user.id)
    sessions[message.from_user.id] = school
    new_or_old_user_check_and_create(message.from_user.id, message.from_user.username)
    if check_user_is_allowed(message.from_user.id):
        if not user_has_settings(message.from_user.id):
            init_settings(message.from_user.id)
        await message.answer(
            "Привет! Я *бот*, _созданный_ с помощью aiogram.\n Пиши /help если нужна помощь",
            parse_mode="Markdown",
        )
        await message.answer("Выберите действие:", reply_markup=keyboard_inline_start())
    else:
        await message.answer(
            "Вы не можете пользоваться ботом, попросите администраторов включить вас в белый список."
        )


def init_settings(telegram_id):
    default_settings = {'boolean_notify_new_answers': False,
                        'boolean_notify_new_homework': False,
                        'boolean_notify_admins': True}
    for key, value in default_settings.items():
        add_settings(telegram_id, key, value)


@router.message(Command("help"))
@router.message(F.text.lower() == "помощь")
async def help(message: Message):
    await message.answer(
        "Команды:\n<b>/start</b> - начать работу с ботом\n<i>/help</i> - получить помощь<a href='https://google.com'>hello</a>\n/about - узнать о боте",
        parse_mode="HTML",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(Command("about"))
async def about(message: Message):
    await message.answer(f"разработка бота. Твое имя {message.from_user.first_name}")


####################### NETSCHOOL #############################

@router.callback_query(lambda c: c.data == "log_in")
async def log_in(callback: CallbackQuery, state: FSMContext):
    try:
        school = sessions.get(callback.from_user.id)
        if not school:
            school = School(login="", password="", user_id=callback.from_user.id)
            sessions[callback.from_user.id] = school
        if not school.active:
            await callback.message.answer("Авторизация на сайт netschool\nВведите номер телефона(+7)",
                                          reply_markup=keyboard_back())
            await state.set_state(Auth.login)
            await callback.answer()
        else:
            await callback.message.answer("Вы уже авторизованы!", reply_markup=keyboard_logout())

    except Exception as e:
        await callback.message.answer("/start")
    await callback.answer()


@router.message(Auth.login, F.text)
async def netschool_login(message: Message, state: FSMContext):
    phone = message.text.strip()

    if not (phone.startswith("+7") and len(phone) == 12 and phone[1:].isdigit()):
        await message.answer("Введите корректный номер телефона.\n""Пример: +79991234567", reply_markup=keyboard_back())
        return

    await state.update_data(login=phone)

    await message.answer("Отлично!\nВведите пароль:", reply_markup=keyboard_back())
    await state.set_state(Auth.password)


@router.message(Auth.password, F.text)
async def netschool_password(message: Message, state: FSMContext):
    await state.update_data(password=message.text)
    data = await state.get_data()
    login = data["login"]
    password = data["password"]

    await message.delete()

    # получили месседж и теперь создаем коробку, в словарик кладем [ид месседжа и значение]
    #  коробка сущесвует но значение пустое

    # в библиотеке netchool_cap есть специальный метод otp_callback, он работает по принципу если он не None
    #  то смс сообщения нужно вводить не в консоль а через свою функцию
    async def sms_user(mfa, mfa_info):
        future = asyncio.get_event_loop().create_future()
        sms_feature[message.from_user.id] = future
        await message.answer("Введите sms:", reply_markup=keyboard_back())
        await state.set_state(Auth.sms)
        return await future

    # sms_user мы передаем в сам класс, функция отрабатывает и отдает коробку уже библиотеке

    school = sessions[message.from_user.id]
    school.log = login
    school.password = password
    school.otp_callback = sms_user

    async def log_school():
        try:
            await school.login()
            sessions[message.from_user.id] = school
            await message.answer("успешно вошел", reply_markup=keyboard_logout())
        except Exception as e:
            await message.answer(f"{e}")

    asyncio.create_task(log_school())


@router.message(F.text == "Разлогин")
async def logout_sch(message: Message, state: FSMContext):
    print(sessions)
    if message.from_user.id not in sessions:
        await message.answer(text="Авторизуйтесь")
    else:
        print("разлогин")
        await state.clear()
        school = sessions[message.from_user.id]
        await school.logout()
        del sessions[message.from_user.id]
        await message.answer(text="Успешный разлогин")


@router.message(Auth.sms, F.text)
async def netschool_sms(message: Message, state: FSMContext):
    await state.update_data(sms=message.text)
    data = await state.get_data()
    sms = data["sms"]

    # теперь мы получили смс и заполняем коробку(значение в коробке теперь не пустое)
    future = sms_feature[message.from_user.id]
    if future and not future.done():
        future.set_result(sms)
########################################################################################


@router.message(Command("test"))
async def test(message: Message):
    await send_notify_to_users(message.bot, "boolean_notify_admins", 'Лох', 'ТЫ Лох')
    await message.answer("Done!")


@router.message()
async def talk(message: Message):
    await message.answer("Неизвестная команда!", reply_markup=keyboard_reply_help())
