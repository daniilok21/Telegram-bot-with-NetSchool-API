from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    waiting_date = State()
    waiting_homework_answer = State()
    waiting_homework_content = State()
    selected_date = State()
    answer = State()
    waiting_get_hw_date = State()
    waiting_get_ht_date_netschool = State()
    waiting_get_ht_date_student = State()
    waiting_add_ht_date_student = State()


class Auth(StatesGroup):
    login = State()
    password = State()
    sms = State()