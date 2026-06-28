import asyncio
from datetime import date

from data import db_session
from data.db_manager import create_check_netschool_session
from data.encoder import decrypt
from data.sessions import Session
from netschool_cap import NetSchool


# logging.basicConfig(level=logging.DEBUG)
MONTHS = {
    1: "января", 2: "февраля", 3: "марта", 4: "апреля",
    5: "мая", 6: "июня", 7: "июля", 8: "августа",
    9: "сентября", 10: "октября", 11: "ноября", 12: "декабря"
}

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

        y, m, d = dat.year, dat.month, dat.day
        diary = await self.ns.diary(start=date(y, m, d), end=date(y, m, d))
        lines = []
        if diary:
            # Заголовок с датой
            dt = diary.start.strftime("%d.%m.%Y")
            lines.append(f"📅 <b>На {dt}</b>")
            lines.append("➖➖➖➖➖➖➖➖➖➖")

            tasks_found = False

            for day in diary.schedule:
                for lesson in day.lessons:
                    homework = [asg.content for asg in lesson.assignments if asg.kind_abbr == "ДЗ"]
                    if homework:
                        tasks_found = True

                        subject_text = f"📌 <b>{lesson.subject}</b>"
                        tasks_text = f"📝 <i>{'; '.join(homework)}</i>"

                        lines.append(f"{subject_text}\n{tasks_text}")
                        lines.append("─────────────────────────")

            if tasks_found:
                return "\n".join(lines)

            return f"📅 <b>На {dt}</b>\n➖➖➖➖➖➖➖➖➖➖\n✅ <i>Домашних заданий нет</i>"

    async def show_all_subjects(self, flag=False):
        try:
            subjects = await self.ns.subjects()
            if not flag:
                return "\n".join(f"`{subject.name}`" for subject in subjects)
            return [subject.name for subject in subjects]
        except Exception:
            print("ваша сессия закночилась\nавторизуйтесь заново")

    async def get_average_subject(self, subject: str, period: int):
        if period == 1:
            marks = await self.ns.term_grades(date(2025, 9, 1), date(2025, 12, 31),
                                                 subject=subject)
        elif period == 2:
            marks = await self.ns.term_grades(date(2026, 1, 1), date(2026, 8, 31),
                                              subject=subject)
        else:
            print("ошибка")
            return None
        lines = []
        for subject_grades in marks:

            lines.append(f"<b>📖 Предмет: {subject_grades.subject.upper()}</b>")
            lines.append("<code>─────────────────────────</code>")

            for dt, mark, weight in subject_grades.marks:
                dat = f"{dt.day:02d}.{dt.month:02d}.{dt.year}"

                lines.append(f"• <code>{dat}</code> — оценка: <b>{mark}</b> (вес: <code>{weight}</code>)")

            lines.append("<code>─────────────────────────</code>")
            lines.append(f"📊 Средний: <code>{subject_grades.average:.2f}</code>")
            lines.append(f"⚖️ Ср. взвеш.: <code>{subject_grades.weighted_average:.2f}</code>")
            lines.append("\n")

        # Соединяем в одну строку
        return "\n".join(lines)
