from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import aiosqlite
from datetime import datetime
import asyncio

class VacancyParser:
    def __init__(self):
        self.db_path = 'vacancies.db'

    async def create_tables(self):
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute('''
                CREATE TABLE IF NOT EXISTS vacancies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME,
                    count INTEGER,
                    change INTEGER
                )
            ''')
            await db.commit()

    def get_vacancy_count(self):
        url = 'https://robota.ua/zapros/junior/ukraine'
        driver = webdriver.Safari()
        driver.get(url)

        try:
            # Чекати, поки елемент з'явиться на сторінці
            element = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.XPATH,
                                                "/html/body/app-root/div/alliance-jobseeker-vacancies-root-page/div/alliance-jobseeker-desktop-vacancies-page/main/section/div/div/lib-desktop-top-info/div/div[1]"))
            )

            html = driver.page_source
            print(html)  # Додано для виведення HTML-коду сторінки
            soup = BeautifulSoup(html, 'html.parser')

            # Знайти елемент, який містить кількість вакансій
            count_element = soup.find('div', class_='santa-typo-h2 santa-mr-10').text.strip()
            count = int(''.join(filter(str.isdigit, count_element)))  # Видалення всіх нецифрових символів
            print(f"Parsed vacancy count: {count}")  # Додано для налагодження
            return count
        except Exception as e:
            print(f"Error occurred: {e}")
            return None
        finally:
            driver.quit()  # Закриття браузера у будь-якому випадку

    async def save_to_db(self, count):
        async with aiosqlite.connect(self.db_path) as db:
            # Отримати попереднє значення кількості вакансій
            async with db.execute('SELECT count FROM vacancies ORDER BY timestamp DESC LIMIT 1') as cursor:
                previous_count = await cursor.fetchone()
            if previous_count:
                previous_count = previous_count[0]
                change = count - previous_count
            else:
                change = 0

            timestamp = datetime.now()
            await db.execute("INSERT INTO vacancies (timestamp, count, change) VALUES (?, ?, ?)",
                             (timestamp, count, change))
            await db.commit()
            print(f"Saved to DB: {timestamp}, {count}, {change}")  # Додано для налагодження

    async def main_parser(self):
        await self.create_tables()
        while True:
            count = self.get_vacancy_count()
            if count is not None:
                await self.save_to_db(count)
                print(f"Кількість вакансій: {count}")
            await asyncio.sleep(3600)  # Чекати 1 годину перед наступним парсингом

# Одноразовий запуск парсера для тестування
if __name__ == "__main__":
    parser = VacancyParser()
    asyncio.run(parser.main_parser())
