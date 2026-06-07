import sqlalchemy.orm
from sqlalchemy import func, Column, Integer, String, Boolean, Float, BigInteger, Text, DateTime, ForeignKey
from data.db_session import SqlAlchemyBase
from datetime import datetime

class Session(SqlAlchemyBase):
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.now(), nullable=True)
    user = sqlalchemy.orm.relationship("User", back_populates="sessions")

    def to_dict(self, only=()):
        fields = {
            'id': self.id,
            'user_id': self.user_id,
            'session_token': self.session_token,
            'created_at': self.created_at
        }
        if only:
            return {key: fields[key] for key in only}
        return fields