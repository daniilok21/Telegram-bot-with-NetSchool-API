import sqlalchemy.orm
from sqlalchemy import func, Column, Integer, String, Boolean, Float, BigInteger, Text, DateTime, ForeignKey
from data.db_session import SqlAlchemyBase


class HomeworkAnswer(SqlAlchemyBase):
    __tablename__ = 'homework_answers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    subject = Column(String(100), nullable=False)
    date = Column(String(10), nullable=False, index=True)
    text = Column(Text, nullable=True)
    file_id = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)

    user = sqlalchemy.orm.relationship("User", back_populates="homework_answers")

    def to_dict(self, only=()):
        fields = {
            'id': self.id,
            'user_id': self.user_id,
            'subject': self.subject,
            'date': self.date,
            'text': self.text,
            'file_id': self.file_id,
            'created_at': self.created_at
        }
        if only:
            return {key: fields[key] for key in only}
        return fields