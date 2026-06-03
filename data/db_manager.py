from sqlalchemy import false

from . import db_session
from .users import User


def new_or_old_user_check_and_create(telegram_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        is_administrator = User.telegram_id == '5126480415' or User.telegram_id == '2078101725'
        user = User(
            telegram_id=User.telegram_id,
            is_allowed=is_administrator,
            is_admin=is_administrator
        )
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



def chech_user_is_admin(telegram_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        db_sess.close()
        return False
    is_admin = user.is_admin
    db_sess.close()

    return is_admin