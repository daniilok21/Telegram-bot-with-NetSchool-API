from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

from data.db_manager import get_settings, get_all_subjects


def keyboard_inline_start():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📚 Посмотреть ДЗ", callback_data="view_ht"),
                InlineKeyboardButton(
                    text="📖 Посмотреть ответы", callback_data="view_answer_ht"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="➕ Создать ДЗ", callback_data="add_ht_student"
                ),
                InlineKeyboardButton(
                    text="➕ Добавить ответ", callback_data="add_answer_ht"
                ),
            ],
            [
                InlineKeyboardButton(text="📊 Средний балл", callback_data="average_score"),
                InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings"),
            ],
        ]
    )
    return keyboard


def keyboard_inline_subjects():
    keyboard_markup = []
    row = []
    count = 0
    subjects = get_all_subjects()
    if subjects:
        for i in subjects:
            count += 1
            row.append(InlineKeyboardButton(text=f'{i["name"]}', callback_data=f'subject_{i["id"]}'))
            if count == 2:
                keyboard_markup.append(row.copy())
                row.clear()
                count = 0
        if row:
            keyboard_markup.append(row.copy())
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=keyboard_markup
        )
    else:
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Предметов не нашлось!', callback_data="back")]
            ]
        )
    return keyboard


def keyboard_inline_view_hw():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📖 На завтра", callback_data="all_hw_tomorrow"
                ),
                InlineKeyboardButton(
                    text="🔍 По дате", callback_data="get_hw_date"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📚 По предмету", callback_data="get_hw_subject"
                ),
                InlineKeyboardButton(
                    text="◀️ Назад ", callback_data="back"
                ),
            ]
        ]
    )
    return keyboard


def keyboard_inline_view_ht():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="📖 Из NetSchool", callback_data="get_ht_netschool"
                ),
                InlineKeyboardButton(
                    text="👤 От учеников", callback_data="get_ht_students"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📚 По предмету", callback_data="get_ht_subject"
                ),
                InlineKeyboardButton(
                    text="◀️ Назад ", callback_data="back"
                ),
            ]
        ]
    )
    return keyboard


def keyboard_save():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Завершить", callback_data="save_hw"),
                InlineKeyboardButton(text="Отмена", callback_data="back"),
            ]
        ]
    )
    return keyboard


def keyboard_save_ht():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Завершить", callback_data="save_ht"),
                InlineKeyboardButton(text="Отмена", callback_data="back"),
            ]
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
                InlineKeyboardButton(
                    text="🔍 Поиск по дате", callback_data="get_hw_date"
                ),
                InlineKeyboardButton(
                    text="📚 По предмету", callback_data="get_hw_subject"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="◀️ Назад", callback_data="back"
                ),
            ]
        ]
    )
    return keyboard

def keyboard_after_get_ht_student():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="back"),
                InlineKeyboardButton(
                    text="🔍 Поиск по дате", callback_data="get_ht_date_student"
                ),
            ],
        ]
    )
    return keyboard

def keyboard_back():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="back"),
            ],
        ]
    )
    return keyboard

def keyboard_after_get_ht():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="◀️ Назад", callback_data="back"),
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

def keyboard_settings_menu():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🔔 Уведомления", callback_data="notify"),
             InlineKeyboardButton(text="👤 Авторизоваться", callback_data="log_in"),
        ],
        [
            InlineKeyboardButton(text="◀️ Назад", callback_data="back")],
        ]
    )
    return keyboard


def keyboard_settings_notify(telegram_id):
    notify_settings_name = ['boolean_notify_new_answers',
                       'boolean_notify_new_homework',
                       'boolean_notify_admins']
    settings_value = get_settings(telegram_id ,notify_settings_name)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{'✅' if settings_value['boolean_notify_admins'] else '❌'} Уведомления админов", callback_data="toggle_notify_admins")],
            [InlineKeyboardButton(text=f"{'✅' if settings_value['boolean_notify_new_answers'] else '❌'} Новые ответы", callback_data="toggle_notify_new_answers")],
            [InlineKeyboardButton(text=f"{'✅' if settings_value['boolean_notify_new_homework'] else '❌'} Новые ДЗ", callback_data="toggle_notify_new_homework")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back")]
        ]
    )
    return keyboard