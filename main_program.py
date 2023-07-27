import telebot # модуль для Telegram
from datetime import datetime, timezone, timedelta

import sqlite3 as sl # модуль для работы с базой данных

# указываем токен для доступа к боту
bot = telebot.TeleBot('6468009909:AAG2h09X6yA1TfkadxV7JCbQsVMqU69-Rbw')
start_text = "Привет, это makhov-report-v-1-bot \n\n пиши сюда свои отчеты за день, а я их буду сохранять"
con = sl.connect('reports.db') # подключаемся к файлу с базой данных

with con: # открываем файл
    # получаем кол-во таблиц с нужным именем
    data = con.execute("select count(*) from sqlite_master where type='table' and name='reports'") # выполняем sql-запрос
    for row in data:
        if row[0] == 0:
            # создаем таблицу для отчетов
            with con:
                con.execute("""
                    CREATE TABLE reports (
                        datetime VARCHAR(40) PRIMARY KEY,
                        date VARCHAR(20),
                        id VARCHAR(20),
                        name VARCHAR(200),
                        text VARCHAR(500))
                """)

# обрабатываем старт бота
@bot.message_handler(commands=['start'])
def start(message):
    # выводим приветсвенное сообщение
    bot.send_message(message.from_user.id, start_text, parse_mode='Markdown')


@bot.message_handler(content_types=['text']) # функция func будет вызываться каждый раз, когда входящее сообщение от пользователя будет содержать текст.
def func(message):
    con = sl.connect('reports.db') # подключаемся к базе
    sql = "INSERT INTO reports (datetime, date, id, name, text) values(?, ?, ?, ?, ?)" # подготавливаем запрос
    time_now = datetime.now(timezone.utc) # получаем время
    date = time_now.date() # получаем дату
    data = [
        (str(time_now), str(date), str(message.from_user.id), str(message.from_user.username), str(message.text[:500]))
    ]
    # добавляем с помощью запроса данные
    with con:
        con.executemany(sql, data)
    # отправляем пользователю сообщение о том, что отчет принят
    bot.send_message(message.from_user.id, 'Отчет принят!', parse_mode='Markdown')


# запуск бота
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, interval=0)
        except Exception as e:
            print('Сработало исключение!')
