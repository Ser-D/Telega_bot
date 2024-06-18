import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
import aiosqlite
from datetime import date
import asyncio

API_TOKEN = '7343738222:AAEYTLHeDVEdC6uzS-E5guG7XzBrfF2KUng'

# Створення об'єктів бота і диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

async def get_today_vacancies():
    async with aiosqlite.connect('vacancies.db') as db:
        today = date.today()
        async with db.execute("SELECT * FROM vacancies WHERE date(timestamp) = ?", (today,)) as cursor:
            rows = await cursor.fetchall()
    print(f"Data retrieved: {rows}")  # Додано для налагодження
    return rows

# Функція створення кнопки
def create_statistic_button():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Statistic", callback_data="get_statistic")]
        ]
    )
    return keyboard

# Команда /get_today_statistic
@dp.message(Command("get_today_statistic"))
async def send_today_statistic(message: Message):
    data = await get_today_vacancies()
    if data:
        df = pd.DataFrame(data, columns=['ID', 'Timestamp', 'Count', 'Change'])
        file_path = 'vacancy_report.xlsx'
        df.to_excel(file_path, index=False)

        # Використання FSInputFile для відправки файлу
        input_file = FSInputFile(file_path)
        await message.answer_document(input_file)
    else:
        await message.answer("Сьогодні не знайдено жодних даних.")

# Команда /start
@dp.message(Command("start"))
async def send_welcome(message: Message):
    keyboard = create_statistic_button()
    await message.answer("Welcome! Use the button below to get today's statistics.", reply_markup=keyboard)

# Обробник натискання кнопки
@dp.callback_query(lambda c: c.data == 'get_statistic')
async def process_callback_button(callback_query: CallbackQuery):
    await send_today_statistic(callback_query.message)
    await callback_query.answer()

# Запуск бота
if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)
