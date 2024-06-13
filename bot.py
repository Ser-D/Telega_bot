import sqlite3
from datetime import date, datetime
import pandas as pd
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command

API_TOKEN = '7343738222:AAEYTLHeDVEdC6uzS-E5guG7XzBrfF2KUng'

# Створення об'єктів бота і диспетчера
bot_instance = Bot(token=API_TOKEN)
dp = Dispatcher()

# Функція створення кнопки
def create_statistic_button():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Statistic", callback_data="get_statistic")]
        ]
    )
    return keyboard

# Функція для збереження статистики користувача
def save_user_statistics(user_id, username, command, message_text):
    conn = sqlite3.connect('statistics.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS user_statistics
                 (timestamp DATETIME, user_id INTEGER, username TEXT, command TEXT, message_text TEXT)''')
    timestamp = datetime.now()
    c.execute("INSERT INTO user_statistics (timestamp, user_id, username, command, message_text) VALUES (?, ?, ?, ?, ?)",
              (timestamp, user_id, username, command, message_text))
    conn.commit()
    conn.close()

# Асинхронна функція для отримання даних за сьогоднішню дату
async def get_today_statistics():
    conn = sqlite3.connect('vacancies.db')
    c = conn.cursor()
    today = date.today()
    c.execute("SELECT * FROM vacancies WHERE date(timestamp) = ?", (today,))
    rows = c.fetchall()
    conn.close()
    return rows

# Команда /get_today_statistic
@dp.message(Command("get_today_statistic"))
async def send_today_statistic(message: Message):
    # Збереження статистики користувача
    save_user_statistics(message.from_user.id, message.from_user.username, "/get_today_statistic", message.text)

    data = await get_today_statistics()
    if data:
        df = pd.DataFrame(data, columns=['Timestamp', 'Count', 'Change'])
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
    # Збереження статистики користувача
    save_user_statistics(message.from_user.id, message.from_user.username, "/start", message.text)

    keyboard = create_statistic_button()
    await message.answer("Welcome! Use the button below to get today's statistics.", reply_markup=keyboard)

# Обробник натискання кнопки
@dp.callback_query(lambda c: c.data == 'get_statistic')
async def process_callback_button(callback_query: CallbackQuery):
    # Збереження статистики користувача
    save_user_statistics(callback_query.from_user.id, callback_query.from_user.username, "button_statistic", callback_query.message.text)

    await send_today_statistic(callback_query.message)
    await callback_query.answer()
