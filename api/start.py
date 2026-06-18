import asyncio

from sqlalchemy.util.typing import NoneType
from data.db_manager import create_check_netschool_session
from netschool_cap import NetSchool, Day
import logging
from datetime import date, datetime
from data.sessions import Session
from data import db_session
from data.encoder import decrypt
# logging.basicConfig(level=logging.DEBUG)



class School:
    def __init__(self, user_id, login, password, school="МБОУ «Средняя общеобразовательная школа №10» г. Канаш"):
        self._log = login
        self._password = password
        self.school = school
        self.active = False
        self.ns = NetSchool("https://net-school.cap.ru/")
        self.otp_callback = None
        self.user_id = user_id
        self.session = None
        self._ready = asyncio.Event()
        asyncio.create_task(self._init())

    async def _init(self):
        db_sess = db_session.create_session()
        session = db_sess.query(Session).filter(Session.user_id == self.user_id).first()
        db_sess.close()
        if not session:
            print("неактивная сессия")
            self.active = False
        else:
            if session:
                session_token = session.session_token
                try:
                    await self.ns.import_session(decrypt(session_token))
                    self.active = True
                    print("вошел по сессии")  
                except Exception as e:
                    print(f"error: {e}")
        self._ready.set()

    async def _wait_init(self):
        await self._ready.wait()


    async def login(self):
            await self.ns.login_via_gosuslugi(
                esia_login=self._log,
                esia_password=self._password,
                school=self.school,
                otp_callback=self.otp_callback
            )
            session = self.ns.export_session()
            create_check_netschool_session(session=session, user_id=self.user_id)
            self.active = True
            print("вошел по смс")
        
    
    async def logout(self):
        if self.active:
            await self.ns.logout()
            db_sess = db_session.create_session()
            db_sess.query(Session).filter(Session.user_id == self.user_id).delete()
            db_sess.commit()
            print("вышел")
            self.active = False

    async def today_homework(self, dat):
        y, m, d = map(int, dat.split(', '))
        diary = await self.ns.diary(start=date(y, m, d), end=date(y, m, d))
        lines = []
        if diary:
            lines.append("🎒 Домашние задания")
            for day in diary.schedule:
                for lessons in day.lessons:
                    homework = [asg.content for asg in lessons.assignments if asg.kind_abbr == "ДЗ"]
                    line = "\t"+"📌" + str(lessons.subject)+"\n"+"\t"+"📝   "+" ".join(homework)+"\n"
                    lines.append(line)
        else:  
            return "Без ДЗ"

        return "\n".join(lines)

    
  
        
