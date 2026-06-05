import sqlalchemy.orm
from datetime import datetime
from sqlalchemy import func, Column, Integer, String, Boolean, Float, BigInteger, Text, DateTime
from data.db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True, index=True)
    login = Column(String(255), nullable=True)
    session_data = Column(Text, nullable=True)
    is_allowed = Column(Boolean, default=False, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)

    sessions = sqlalchemy.orm.relationship("Session", back_populates="user", cascade="all, delete-orphan")
    homework_answers = sqlalchemy.orm.relationship("HomeworkAnswer", back_populates="user", cascade="all, delete-orphan")

    sessions = sqlalchemy.orm.relationship("Session", back_populates="user", cascade="all, delete-orphan")
    homework_answers = sqlalchemy.orm.relationship("HomeworkAnswer", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self, only=()):
        fields = {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'username': self.username,
            'login': self.login,
            'session_data': self.session_data,
            'is_allowed': self.is_allowed,
            'is_admin': self.is_admin,
            'created_at': self.created_at.strftime("%d.%m.%Y %H:%M") if self.created_at else None
        }
        if only:
            return {key: fields[key] for key in only}
        return fields
