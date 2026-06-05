from . import db_session
from .users import User
from .homework_answers import HomeworkAnswer


def add_hw(telegram_id, subject, date, text=None, files=None):
    db_sess = db_session.create_session()

    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()
    if not user:
        return False

    homework = HomeworkAnswer(
        user_id=user.id,
        subject=subject,
        date=date,
        text=text,
    )
    if files:
        homework.set_files(files)
    db_sess.add(homework)
    db_sess.commit()

    db_sess.close()
    return True


def get_hw(date, subject=None):
    db_sess = db_session.create_session()

    res = db_sess.query(HomeworkAnswer).filter(HomeworkAnswer.date == date)
    if subject:
        res = res.filter(HomeworkAnswer.subject == subject)
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
    if not user:
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