from . import db_session
from .homework_tasks import HomeworkTask
from .users import User
from .homework_answers import HomeworkAnswer
from .sessions import Session
from .encoder import *
from .settings import Setting
from .subjects import Subject


def init_subjects(subjects):
    db_sess = db_session.create_session()
    for subject_name in subjects:
        already = db_sess.query(Subject).filter(Subject.name == subject_name).first()

        if not already:
            subj = Subject(name=subject_name, is_active=True)
            db_sess.add(subj)
    db_sess.commit()
    db_sess.close()

def get_or_create_subject(subject_name):
    db_sess = db_session.create_session()

    subject = db_sess.query(Subject).filter(Subject.name == subject_name).first()

    if not subject:
        subject = Subject(name=subject_name)
        db_sess.add(subject)
        db_sess.commit()

    subject_id = subject.id
    db_sess.close()
    return subject_id


def get_subject_by_id(subject_id):
    db_sess = db_session.create_session()

    subject = db_sess.query(Subject).filter(Subject.id == subject_id).first()

    if not subject:
        return False

    db_sess.close()
    return subject.name


def get_all_subjects():
    db_sess = db_session.create_session()
    subjects = db_sess.query(Subject).filter(Subject.is_active == True).order_by(Subject.name).all()
    result = [s.to_dict() for s in subjects]
    db_sess.close()
    return result


def set_is_active_subject(subject_id, is_active):
    db_sess = db_session.create_session()

    subject = db_sess.query(Subject).filter(Subject.id == subject_id).first()
    if not subject:
        db_sess.close()
        return False

    subject.is_active = is_active
    db_sess.commit()
    db_sess.close()
    return True


def get_user_by_telegram_id(telegram_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()
    db_sess.close()
    return user


def get_users_notify_settings(setting_name):
    db_sess = db_session.create_session()

    settings = db_sess.query(Setting).filter(
        Setting.setting_name == setting_name,Setting.is_enabled == True).all()

    res = []
    for setting in settings:
        user = db_sess.query(User).filter(User.telegram_id == setting.telegram_id).first()
        if user:
            res.append(user)

    db_sess.close()
    return res


async def send_notify_to_users(bot, setting_name, title, message, inline_keyboard=None, except_user_id=None):
    users = get_users_notify_settings(setting_name)

    for user in users:
        if except_user_id and user.telegram_id == except_user_id:
            continue

        text = f"🔔 {title}\n\n{message}"
        await bot.send_message(
            chat_id=user.telegram_id,
            text=text,
            reply_markup=inline_keyboard
        )

def get_settings(telegram_id, settings_names : list):
    db_sess = db_session.create_session()

    settings = db_sess.query(Setting).filter(
        Setting.telegram_id == telegram_id, Setting.setting_name.in_(settings_names)).all()

    res = {}
    if settings:
        for setting in settings:
            if setting.setting_name.startswith("boolean_"):
                res[setting.setting_name] = setting.is_enabled
            else:
                res[setting.setting_name] = setting.setting_value

    db_sess.close()
    return res

def user_has_settings(telegram_id):
    db_sess = db_session.create_session()
    setting = db_sess.query(Setting).filter(Setting.telegram_id == telegram_id).first()
    db_sess.close()

    return setting


def add_settings(telegram_id, settings_name, value):
    db_sess = db_session.create_session()

    setting = db_sess.query(Setting).filter(
        Setting.telegram_id == telegram_id, Setting.setting_name == settings_name).first()

    if setting:
        if settings_name.startswith("boolean_"):
            setting.is_enabled = value
        else:
            setting.setting_value = value
    else:
        new_setting = Setting(
            telegram_id=telegram_id,
            setting_name=settings_name
        )
        if settings_name.startswith("boolean_"):
            new_setting.is_enabled = value
        else:
            new_setting.setting_value = value
        db_sess.add(new_setting)

    db_sess.commit()
    db_sess.close()
    return True


def add_hw(telegram_id, subject, date, text=None, files=None):
    db_sess = db_session.create_session()

    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        return False

    subject_id = get_or_create_subject(subject);

    homework = HomeworkAnswer(
        user_id=user.id,
        subject_id=subject_id,
        date=date,
        text=text,
    )
    if files:
        homework.set_files(files)
    db_sess.add(homework)
    db_sess.commit()

    db_sess.close()
    return True


def get_hw(date, subject_name=None):
    db_sess = db_session.create_session()

    res = db_sess.query(HomeworkAnswer).filter(HomeworkAnswer.date == date)
    if subject_name:
        subject = db_sess.query(Subject).filter(Subject.name == subject_name).first()
        if subject:
            res = res.filter(HomeworkAnswer.subject_id == subject.id)
    res.order_by(HomeworkAnswer.created_at)

    homework = res.all()

    result = {}
    for h in homework:
        user_name = h.user.username if h.user and h.user.username else f"User_{h.user_id}"
        if user_name not in result:
            result[user_name] = []
        result[user_name].append(h.to_dict())
    db_sess.close()
    return result


def add_ht(subject, date, title=None, description=None, files=None, telegram_id=None):
    db_sess = db_session.create_session()

    subject_id = get_or_create_subject(subject)

    task = HomeworkTask(
        subject_id=subject_id,
        date=date,
        title=title,
        description=description
    )
    if telegram_id:
        user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()
        if not user:
            return False
        task.user_id = user.id

    if files:
        task.set_files(files)
    db_sess.add(task)
    db_sess.commit()
    db_sess.close()
    return True


def get_ht(date, isFromNetSchool, subject_name=None):
    db_sess = db_session.create_session()

    res = db_sess.query(HomeworkTask).filter(HomeworkTask.date == date)
    if subject_name:
        subject = db_sess.query(Subject).filter(Subject.name == subject_name).first()
        if subject:
            res = res.filter(HomeworkTask.subject_id == subject.id)

    if isFromNetSchool:
        res = res.filter(HomeworkTask.user_id == None)
    else:
        res = res.filter(HomeworkTask.user_id != None)

    hometask = res.all()

    result = {}
    for h in hometask:
        if h.user_id:
            user_name = h.user.username if h.user and h.user.username else f"User_{h.user_id}"
        else:
            user_name = "NetSchool"
        if user_name not in result:
            result[user_name] = []
        result[user_name].append(h.to_dict())

    db_sess.close()
    return result

def new_or_old_user_check_and_create(telegram_id, username):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        is_administrator = telegram_id == 5126480415 or telegram_id == 2078101725
        user = User(
            telegram_id=telegram_id,
            username=username,
            is_allowed=is_administrator,
            is_admin=is_administrator
        )
        db_sess.add(user)
        db_sess.commit()
    else:
        if user.username != username and username:
            user.username = username
            db_sess.commit()
    db_sess.close()
    return user
    
def create_check_netschool_session(user_id, session):
    db_sess = db_session.create_session()
    school = db_sess.query(Session).filter(Session.user_id == user_id).first()
    if not school:
        school = Session(
            user_id = user_id,
            session_token = encrypt(session)
        )

        db_sess.add(school)
        db_sess.commit()



def check_user_is_allowed(telegram_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        db_sess.close()
        return False
    is_allowed = user.is_allowed
    db_sess.close()

    return is_allowed


def give_user_allowed(telegram_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        db_sess.close()
        return False

    user.is_allowed = True

    db_sess.commit()
    db_sess.close()
    return True


def deny_user_allowed(telegram_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()
    if not user or user.is_admin:
        db_sess.close()
        return False

    user.is_allowed = False

    db_sess.commit()
    db_sess.close()
    return True


def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    db_sess.close()
    return [user.to_dict() for user in users]


def check_user_is_admin(telegram_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        db_sess.close()
        return False
    is_admin = user.is_admin
    db_sess.close()

    return is_admin