from dataclasses import fields

import sqlalchemy.orm
from datetime import datetime
from sqlalchemy import func, Column, Integer, String, Boolean, Float, BigInteger, Text, DateTime, ForeignKey
from data.db_session import SqlAlchemyBase
import json


class HomeworkTask(SqlAlchemyBase):
    __tablename__ = 'homework_tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True, index=True)
    subject_id = Column(Integer, ForeignKey('subjects.id'), nullable=False, index=True)
    date = Column(String(10), nullable=False, index=True)
    title = Column(String(500), nullable=True)
    description = Column(Text, nullable=True)
    files_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    user = sqlalchemy.orm.relationship("User", back_populates="homework_tasks")
    subject_connection = sqlalchemy.orm.relationship("Subject", back_populates="homework_tasks")

    def set_files(self, files):
        if files:
            self.files_json = json.dumps(files, ensure_ascii=False)
        else:
            self.files_json = None

    def get_files(self):
        if self.files_json:
            return json.loads(self.files_json)
        return []

    def to_dict(self, only=()):
        fields = {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject_connection.name if self.subject_connection else None,
            'date': self.date,
            'title': self.title,
            'description': self.description,
            'files': self.get_files(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if only:
            return {key: fields[key] for key in only}
        return fields