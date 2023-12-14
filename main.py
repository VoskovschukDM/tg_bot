import telebot
import datetime
import json
import pandas as pd
import sqlite3 as sql
from telebot import types
from config import Config, load_config
from bot_token import token
from body import session

config: Config = load_config()
token: str = config.tg_bot.token

bot = telebot.TeleBot(token)
fields_list = ['id', 'state', 'city', 'days', 'auto_warn', 'first_time_auto', 'time_auto', 'city_auto', 'days_auto']
with sql.connect('user_list.db') as con:
    cursor = con.cursor()
    try:
        query = 'CREATE TABLE "users" ("id" INTEGER UNIQUER, "state" TEXT, "city" TEXT, "days" INTEGER,\
         "auto_warn" BOOLEAN, "first_time_auto" TEXT, "time_auto" INTEGER, "city_auto" TEXT, "days_auto" INTEGER, \
         PRIMARY KEY ("id"))'
        cursor.execute(query)
    except:
        pass


def send_msg(currient_bot_session: session, message):
    keyboard = types.ReplyKeyboardMarkup(row_width=len(currient_bot_session.get_buttons()))
    for i in currient_bot_session.get_buttons():
        if i != 'input':
            keyboard.add(types.KeyboardButton(i))
    msg = bot.send_message(message.from_user.id, text=currient_bot_session.get_msg(), reply_markup=keyboard)
    #bot.register_next_step_handler(msg, callback_worker)


#while True:
#    print('%s:%s:%s' % (datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second))
#    if True:
#        #send_auto()

def handler(event,context): # основная функция для обработки действий бота
    body = json.loads(event['body'])
    update = telebot.types.Update.de_json(body)
    bot.process_new_updates([update])

@bot.message_handler(content_types=["text"])
def handl_msg(message):
    print('%s:%s:%s' % (datetime.datetime.now().hour, datetime.datetime.now().minute, datetime.datetime.now().second))
    user_data = {}
    with sql.connect('user_list.db') as con:
        cursor = con.cursor()
        cursor.execute('SELECT id, state, city, days, auto_warn, first_time_auto, time_auto, city_auto, days_auto FROM users WHERE id=={}'.format(message.from_user.id))
        tmp_data = cursor.fetchall()
        if len(tmp_data) == 0:
            tmp_data = [message.from_user.id, 'main_menu', '', 0, False, '', 0, '', 0]
            cursor.execute('INSERT INTO users (id, state, city, days, auto_warn, first_time_auto, time_auto, city_auto, days_auto) \
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', tuple(tmp_data))
            for i in range(len(fields_list)):
                user_data[fields_list[i]] = tmp_data[i]
        else:
            for i in range(len(fields_list)):
                user_data[fields_list[i]] = tmp_data[0][i]
        currient_bot_session = session(message.from_user.id, user_data)

        print(user_data)
        if message.text in currient_bot_session.get_buttons():
            currient_bot_session.button_handler(currient_bot_session.get_buttons().index(message.text), message.from_user.id)
        elif currient_bot_session.waiting_for_input():
            currient_bot_session.input_handler(message.text, message.from_user.id)

        send_msg(currient_bot_session, message)
        currient_bot_session.close_session(user_data)
        cursor.execute('UPDATE users SET id = {id_t}, state = \'{state_t}\', city = \'{city_t}\', days = {days_t}, auto_warn = {auto_warn_t}, first_time_auto = \'{first_time_auto_t}\', time_auto = {time_auto_t}, city_auto = \'{city_auto_t}\', days_auto = {days_auto_t} WHERE id={id_t}'\
        .format(id_t=user_data['id'], state_t=user_data['state'], city_t=user_data['city'], days_t=user_data['days'],\
        auto_warn_t=user_data['auto_warn'], first_time_auto_t=user_data['first_time_auto'], time_auto_t=user_data['time_auto'], \
        city_auto_t=user_data['city_auto'], days_auto_t=user_data['days_auto']))

bot.polling(none_stop=True)
#    else:
#        pass
