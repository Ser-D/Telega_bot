from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime

# Функція для парсингу кількості вакансій з використанням Selenium
def get_vacancy_count():
    url = 'https://www.work.ua/jobs-junior/'
    driver = webdriver.Safari()
    driver.get(url)

    try:
        # Чекати, поки елемент з'явиться на сторінці
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.mt-8.text-default-7 span"))
        )

        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        # Знайти елемент, який містить кількість вакансій
        count_element = soup.find('div', class_='mt-8 text-default-7').find('span')
        if count_element:
            count_text = count_element.text.strip().split()[0]
            count = int(count_text.replace('\u202f', ''))  # Видалити неявні пробіли
            return count
        else:
            print("Element with class 'mt-8 text-default-7' not found.")
            return None
    except Exception as e:
        print(f"Error occurred: {e}")
        return None
    finally:
        driver.quit()

# Функція для оновлення структури таблиці
def update_table():
    conn = sqlite3.connect('vacancies.db')
    c = conn.cursor()
    try:
        c.execute('ALTER TABLE vacancies ADD COLUMN change INTEGER')
    except sqlite3.OperationalError:
        pass  # Стовпець вже існує
    conn.commit()
    conn.close()

# Функція для збереження даних в SQLite
def save_to_db(count):
    if count is None:
        print("No data to save to database.")
        return

    conn = sqlite3.connect('vacancies.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS vacancies
                 (timestamp DATETIME, count INTEGER, change INTEGER)''')

    # Отримати попереднє значення кількості вакансій
    c.execute('SELECT count FROM vacancies ORDER BY timestamp DESC LIMIT 1')
    previous_count = c.fetchone()
    if previous_count:
        previous_count = previous_count[0]
        change = count - previous_count
    else:
        change = 0

    timestamp = datetime.now()
    c.execute("INSERT INTO vacancies (timestamp, count, change) VALUES (?, ?, ?)", (timestamp, count, change))
    conn.commit()
    conn.close()

# Одноразовий запуск парсера для тестування
def test_parser():
    update_table()
    count = get_vacancy_count()
    save_to_db(count)
    if count is not None:
        print(f"Кількість вакансій: {count}")

if __name__ == "__main__":
    test_parser()
