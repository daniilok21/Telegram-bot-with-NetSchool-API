import asyncio
from data.db_manager import create_check_netschool_session
from netschool_cap import NetSchool
import logging
from datetime import date
from data.sessions import Session
from data import db_session
from data.encoder import decrypt
# logging.basicConfig(level=logging.DEBUG)


class School:
    def __init__(self, user_id, login, password, school="МБОУ «Средняя общеобразовательная школа №10» г. Канаш"):
        self.log = login
        self.password = password
        self.school = school
        self.ns = NetSchool("https://net-school.cap.ru/")
        self.otp_callback = None
        self.user_id = user_id
        db_sess = db_session.create_session()
        session = db_sess.query(Session).filter(Session.user_id == self.user_id).first()
        db_sess.close()
        session_token = None
        if session:
            session_token = session.session_token
        self.active = True if session_token else False
        

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
        
    
  
        
