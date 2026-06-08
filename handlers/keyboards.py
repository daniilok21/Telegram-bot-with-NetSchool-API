from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)


def keyboard_inline_start():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📚 Посмотреть ДЗ", callback_data="view_ht"),
                InlineKeyboardButton(
                    text="➕ Добавить ответ на ДЗ", callback_data="add_answer_ht"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📖 Посмотреть ответы на ДЗ", callback_data="view_answer_ht"
                ),
                InlineKeyboardButton(
                    text="📊 Средний балл", callback_data="average_score"
                ),
            ],
            [
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings"),
                InlineKeyboardButton(text="👤 Авторизоваться", callback_data="log_in"),
            ],
        ]
    )
    return keyboard


def keyboard_inline_view_hw():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📖 Все ответы на завтра", callback_data="all_hw_tomorrow"
                ),
                InlineKeyboardButton(
                    text="🔍 Поиск по дате", callback_data="get_hw_date"
                ),
            ],
        ]
    )
    return keyboard


def keyboard_inline_view_ht():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📖 ДЗ через NetSchool", callback_data="get_ht_netschool"
                ),
                InlineKeyboardButton(
                    text="👤 ДЗ от учеников", callback_data="get_ht_students"
                ),
            ],
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
        keyboard=[[KeyboardButton(text="Помощь")]], resize_keyboard=True
    )
    return keyboard


def keyboard_after_get_hw():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data="back"),
                InlineKeyboardButton(
                    text="🔍 Поиск по дате", callback_data="get_hw_date"
                ),
            ],
        ]
    )
    return keyboard

def keyboard_after_get_ht_student():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data="back"),
                InlineKeyboardButton(
                    text="🔍 Поиск по дате ДЗ от пользователей", callback_data="get_ht_date_student"
                ),
            ],
        ]
    )
    return keyboard

def keyboard_back():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data="back"),
            ],
        ]
    )
    return keyboard

def keyboard_after_get_ht():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Назад", callback_data="back"),
                InlineKeyboardButton(
                    text="🔍 Поиск по дате в NetSchool", callback_data="get_ht_date"
                ),
            ],
        ]
    )
    return keyboard


def keyboard_gosuslugi():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data="back_to_check"),
             InlineKeyboardButton(text="👤Авторизоваться", callback_data="go_to_auth")],
        ]
    )
    return keyboard
def keyboard_logout():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Разлогин")]], resize_keyboard=True
    )
    return keyboard