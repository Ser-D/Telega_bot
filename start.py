import asyncio
from parser import VacancyParser
from bot import dp, bot

async def on_startup():
    parser = VacancyParser()
    asyncio.create_task(parser.main_parser())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(on_startup())
