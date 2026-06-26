import asyncio

from sqlalchemy.util.typing import NoneType

from data.db_manager import create_check_netschool_session
from netschool_cap import NetSchool
import logging
from datetime import date, datetime
from data.sessions import Session
from data import db_session
from data.encoder import decrypt
# logging.basicConfig(level=logging.DEBUG)


class School:
    def __init__(
        self,
        user_id,
        login,
        password,
        school="МБОУ «Средняя общеобразовательная школа №10» г. Канаш",
    ):
        self._log = login
        self._password = password
        self.school = school
        self.active = False
        self.ns: Netschool = NetSchool("https://net-school.cap.ru/")
        self.otp_callback = None
        self.user_id = user_id
        self.session = None
        self._ready = asyncio.Event()
        asyncio.create_task(self._init())

    async def _init(self):
        from handlers.routes import unauthorized_sessions, sessions

        db_sess = db_session.create_session()
        session = db_sess.query(Session).filter(Session.user_id == self.user_id).first()
        db_sess.close()
        if not session:
            print("авторизуйтесь")
            self.active = False
            unauthorized_sessions[self.user_id] = self
            return

        session_token = session.session_token
        try:
            print(session_token)
            decrp = decrypt(session_token)
            await self.ns.import_session(decrp)
            self.active = True
            print("вошел по сессии")
            sessions[self.user_id] = self
            print(sessions)
        except Exception as e:
            self.active = False
            print("не авторизован")

            print(f"не авториз сессия{unauthorized_sessions}")

            await self.logout()
            print(f"сессия {self.user_id} удалена")

        self._ready.set()

    async def logout(self):
        from handlers.routes import unauthorized_sessions

        await self.ns.logout()
        db_sess = db_session.create_session()
        db_sess.query(Session).filter(Session.user_id == self.user_id).delete()
        db_sess.commit()
        unauthorized_sessions[self.user_id] = self
        self.active = False

    async def _wait_init(self):
        await self._ready.wait()

    async def login(self):
        from handlers.routes import sessions, unauthorized_sessions

        if unauthorized_sessions.get(self.user_id):
            try:
                await self.ns.login_via_gosuslugi(
                    esia_login=self._log,
                    esia_password=self._password,
                    school=self.school,
                    otp_callback=self.otp_callback,
                )
                sess = self.ns.export_session()
                create_check_netschool_session(session=sess, user_id=self.user_id)
                self.active = True
                print("вошел по смс")

                sessions[self.user_id] = self
                del unauthorized_sessions[self.user_id]
            except Exception as e:
                print(f"error: {e}")

    async def today_homework(self, dat):
        y, m, d = map(int, dat.split(", "))
        diary = await self.ns.diary(start=date(y, m, d), end=date(y, m, d))
        lines = []
        if diary:
            dt = str(diary.start.strftime("%d.%m.%Y"))
            lines.append(dt)
            lines.append("🎒 Домашние задания")
            for day in diary.schedule:
                for lessons in day.lessons:
                    homework = [
                        asg.content
                        for asg in lessons.assignments
                        if asg.kind_abbr == "ДЗ"
                    ]
                    line = (
                        "\t"
                        + "📌"
                        + str(lessons.subject)
                        + "\n"
                        + "\t"
                        + "📝   "
                        + " ".join(homework)
                        + "\n"
                    )
                    lines.append(line)
            if len(lines) > 2:
                return "\n".join(lines)

            return f"{dt}\nНет домашних заданий"

    async def show_all_subjects(self, flag=False):
        try:
            subjects = await self.ns.subjects()
            if not flag:
                return "\n".join(f"`{subject.name}`" for subject in subjects)
            return [subject.name for subject in subjects]
        except Exception:
            print("ваша сессия закночилась\nавторизуйтесь заново")

    async def get_average_subject(self):
        grades = await self.ns.term_grades(
            start=date(2026, 9, 1), end=date(2026, 12, 1)
        )
        result = []
        for g in grades:
            result.append(
                {
                    "subject": g.subject,
                    "average": g.average,
                    "weighted_average": g.weighted_average,
                }
            )
        print(result)
