import asyncio
from netschool_cap import NetSchool
from filek import LOGIN, PASSWORD, SCHOOL
import logging

logging.basicConfig(level=logging.DEBUG)


async def main():
    ns = NetSchool("https://net-school.cap.ru/")
    await ns.login_via_gosuslugi_qr(school=SCHOOL)
    diary = await ns.diary()
    for day in diary.schedule:
        print(dir(day))
        break
    await ns.logout()
    try:
        await ns.diary()
        print("Сессия ещё жива!")
    except Exception:
        print("Вышел из сессии")


asyncio.run(main())
