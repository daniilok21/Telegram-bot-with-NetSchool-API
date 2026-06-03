import db_session
from users import User


def new_or_old_user_check_and_create(telegram_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.telegram_id == telegram_id).first()

    if not user:
        is_administrator = User.telegram_id == 5126480415 or User.telegram_id == 2078101725
        user = User(
            telegram_id=User.telegram_id,
            is_allowed=is_administrator,
            is_admin=is_administrator
        )
    db_sess.close()
    return user
