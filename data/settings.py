import sqlalchemy.orm
from sqlalchemy import func, Column, Integer, String, Boolean, Float, BigInteger, Text, DateTime, ForeignKey
from data.db_session import SqlAlchemyBase
from datetime import datetime


class Setting(SqlAlchemyBase):
    __tablename__ = 'settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(BigInteger, ForeignKey('users.telegram_id'), nullable=False, index=True)
    setting_name = Column(String(100), nullable=False) # имя
    setting_value = Column(String(500), default='') # если нада текстом
    is_enabled = Column(Boolean, default=False) # вкл/выкл
    updated_at = Column(DateTime, default=datetime.now(), onupdate=datetime.now())

    user = sqlalchemy.orm.relationship("User", back_populates="settings")

    def to_dict(self, only=()):
        fields = {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'setting_name': self.setting_name,
            'setting_value': self.setting_value,
            'is_enabled': self.is_enabled,
            'updated_at': self.updated_at if self.updated_at else None,
        }
        if only:
            return {key: fields[key] for key in only}
        return fields

######### setting_name ########### (названия настроек)
# boolean_notify_new_answers (уведомлять о новых ответах)
# boolean_notify_new_homework (уведомлять о новых заданиях)
# boolean_notify_admins (уведомления админов)