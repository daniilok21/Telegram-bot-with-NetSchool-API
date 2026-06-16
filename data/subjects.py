import sqlalchemy.orm
from sqlalchemy import func, Column, Integer, String, Boolean, Float, BigInteger, Text, DateTime, ForeignKey
from data.db_session import SqlAlchemyBase
from datetime import datetime


class Subject(SqlAlchemyBase):
    __tablename__ = 'subjects'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    homework_answers = sqlalchemy.orm.relationship("HomeworkAnswer", back_populates="subject_connection")
    homework_tasks = sqlalchemy.orm.relationship("HomeworkTask", back_populates="subject_connection")

    def to_dict(self, only=()):
        fields = {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active,
            'created_at': self.created_at if self.created_at else None,
        }
        if only:
            return {key: fields[key] for key in only}
        return fields