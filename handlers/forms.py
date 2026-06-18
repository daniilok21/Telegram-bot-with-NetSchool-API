from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    waiting_date = State()
    waiting_hw_subject = State()
    waiting_ht_subject = State()
    waiting_homework_answer = State()
    waiting_hometask = State()
    selected_date = State()
    answer = State()
    current_subject = State()
    waiting_get_hw_date = State()
    waiting_get_ht_date_netschool = State()
    waiting_get_ht_date_student = State()
    waiting_add_ht_date_student = State()


class Auth(StatesGroup):
    login = State()
    password = State()
    sms = State()