import asyncio
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
        self.log = login
        self.password = password
        self.school = school
        self.active = False
        self.ns = NetSchool("https://net-school.cap.ru/")
        self.otp_callback = None
        self.user_id = user_id
        self.init()

    def init(self):
        db_sess = db_session.create_session()
        session = db_sess.query(Session).filter(Session.user_id == self.user_id).first()
        db_sess.close()
        if session:
            self.active = True
            print("активен")

    async def login(self):
        db_sess = db_session.create_session()
        session = db_sess.query(Session).filter(Session.user_id == self.user_id).first()
        db_sess.close()
        if session:
            session_token = session.session_token
            try:
                await self.ns.import_session(decrypt(session_token))
                self.active = True
                print("вошел по сессии")
                return  
            except Exception:
                pass  

        await self.ns.login_via_gosuslugi(
            esia_login=self.log,
            esia_password=self.password,
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
        dt = datetime.strptime(dat, "%Y.%m.%d")
        y, m, d = map(int, str(dt.strftime("%Y, %-m, %-d")).split(', '))
        
        diary = await self.ns.diary(start=date(y, m, d), end=date(y, m, d))
        lines = []
        if diary:
            for day in diary.schedule:
                for lessons in day.lessons:
                    homework = [asg.content for asg in lessons.assignments if asg.kind_abbr == "ДЗ"]
                    line = str(lessons.subject)+"\n"+"Домашка"+"\n"+" ".join(homework)+"\n"
                    lines.append(line)
        else:  
            return "Без ДЗ"

        return "\n".join(lines)

    
  
        
