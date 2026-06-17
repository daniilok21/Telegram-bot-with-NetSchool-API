import asyncio
from datetime import datetime, date

from netschool_cap import NetSchool




async def main():
    async with NetSchool("https://net-school.cap.ru/") as ns:
        await ns.login_via_gosuslugi(esia_login="+79968537517",
                                     esia_password="g5_(7SosR",
                                     school="МБОУ «Средняя общеобразовательная школа №10» г. Канаш")
        for s in await ns.subjects():
            print(s.name)

asyncio.run(main())

