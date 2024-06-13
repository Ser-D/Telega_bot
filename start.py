import asyncio
from bot import bot_instance, dp
from parser import get_vacancy_count, save_to_db

async def main_parser():
    while True:
        count = get_vacancy_count()
        save_to_db(count)
        await asyncio.sleep(3600)  # Чекати 1 годину перед наступним парсингом

async def on_startup():
    asyncio.create_task(main_parser())
    await dp.start_polling(bot_instance)

async def main():
    await on_startup()

if __name__ == "__main__":
    asyncio.run(main())
