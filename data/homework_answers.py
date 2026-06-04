import sqlalchemy.orm
from datetime import datetime
from sqlalchemy import func, Column, Integer, String, Boolean, Float, BigInteger, Text, DateTime, ForeignKey
from data.db_session import SqlAlchemyBase
import json


class HomeworkAnswer(SqlAlchemyBase):
    __tablename__ = 'homework_answers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    subject = Column(String(100), nullable=False)
    date = Column(String(10), nullable=False, index=True)
    text = Column(Text, nullable=True)
    files = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.now(), nullable=False)

    user = sqlalchemy.orm.relationship("User", back_populates="homework_answers")

    def set_files(self, files):
        if files:
            self.files = json.dumps(files, ensure_ascii=False)
        else:
            self.files = None

    def get_files(self):
        if not self.files:
            return []
        return json.loads(self.files)

    def to_dict(self, only=()):
        fields = {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.login if self.user else None,
            'subject': self.subject,
            'date': self.date,
            'text': self.text,
            'files': self.get_files(),
            'created_at': self.created_at
        }
        if only:
            return {key: fields[key] for key in only}
        return fields