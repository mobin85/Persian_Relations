import asyncio
import sys
import re
from datetime import datetime
from aiofiles import os
from httpx import AsyncClient
import aiofiles
from bs4 import BeautifulSoup
from khayyam import JalaliDatetime

YEAR = JalaliDatetime.now().year
URL = f"https://www.time.ir/fa/event/list/0/{YEAR}"
FOLDER_NAME = "relations"


num_month_persian = {
    1: "فروردین",
    2: "اردیبهشت",
    3: "خرداد",
    4: "تیر",
    5: "مرداد",
    6: "شهریور",
    7: "مهر",
    8: "آبان",
    9: "آذر",
    10: "دی",
    11: "بهمن",
    12: "اسفند"
}

num_month_english = {
    1: "farvardin",
    2: "ordibehesht",
    3: "khordad",
    4: "tir",
    5: "mordad",
    6: "shahrivar",
    7: "mehr",
    8: "aban",
    9: "azar",
    10: "dey",
    11: "bahman",
    12: "esfand"
}


async def get_relation_and_write_to_file(month: int) -> None:
    """get relations in a month that given from [1, 12]"""
    if not (1 <= month <= 12):
        sys.exit(1)
    start = datetime.now()
    async with AsyncClient() as client:
        text = (await client.get(f"{URL}/{month}")).text
        soup = BeautifulSoup(text, "html.parser")
        events = (soup.select_one("div.col-md-12").select("li.eventHoliday "))
        async with aiofiles.open(f"./{FOLDER_NAME}/{month}_{num_month_english[month]}.txt", 'w', encoding='utf-8') as f:
            await f.write(f"----- {num_month_persian[month]} -----\n")
            for event in events:
                await f.write(
                    re.sub(r" +", r" ", "\n".join([i.strip(" ") + "\n" for i in event.text.splitlines()])).strip())
            await f.write(f"----- {num_month_persian[month]} -----\n")
    print(f"{num_month_english} done!\ntook {(datetime.now() - start).total_seconds()}S")


async def main():
    coroutines = (get_relation_and_write_to_file(i) for i in range(1, 13))
    print("starting!")
    start = datetime.now()
    try:
        await os.mkdir(FOLDER_NAME)
    except FileExistsError:
        pass
    except Exception as e:
        print(f"there was an error while creating folder {FOLDER_NAME}", e, file=sys.stderr)

    await asyncio.gather(*coroutines)
    print(f"took {(datetime.now() - start).total_seconds()}Seconds to Scrap!")


if __name__ == '__main__':
    asyncio.run(main())
