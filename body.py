from bs4 import BeautifulSoup
import pandas as pd
import requests
import datetime
import logging
from logging import StreamHandler, Formatter
import sys

def get_weather(city: str, day: int):
    result = ''
    if ord(city[0]) in range(1040, 1071):
        city = str(chr(ord(city[0]) + 32)) + city[1:]
    request = requests.get('https://sinoptik.ua/погода-' + city + '/10-дней')
    b = BeautifulSoup(request.text, "html.parser")
    day_urls = b.select('.day-link')[0:(day)]
    for i in range(len(day_urls)):
        request = requests.get('https:' + day_urls[i]['data-link'])
        b = BeautifulSoup(request.text, "html.parser")
        min_arr = b.select('.temperature .min')
        min = min_arr[i].getText()
        max_arr = b.select('.temperature .max')
        max = max_arr[i].getText()
        midday_arr = b.select('.temperature .p5')
        if len(midday_arr) == 0:
            midday_arr = b.select('.temperature .p3')
        midday = midday_arr[0].getText()
        result += 'Темпертаура днём ' + day_urls[i]['data-link'].split('/')[-1] + ': ' + midday + ' ' + min + ' ' + max + '\n'
    return result


class session:
    logging.basicConfig(filename='logs.txt', filemode='a', level=logging.DEBUG)
    logger = logging.getLogger()
    logger.handlers[0].setFormatter(Formatter(fmt='[%(asctime)s] %(levelname)s - \'%(message)s\''))
    logger.setLevel(logging.INFO)

    user = {}

    all_interface_state = {'main_menu': ['Получить погоду по моему городу', 'Получить погоду по выбраному городу', 'Автоматическое оповещение о погоде'],\
                           'today/time_res': ['Вывести погоду на сегодня', 'Вывести погоду на несколько дней', 'Меню'],\
                           'weather_result': ['Меню'],\
                           'city_search': ['Меню', 'input'],\
                           'time_res_choice': ['Меню', 'input'],\
                           'auto_alert_exist': ['Получить информацию по оповещению', 'Сбросить оповещение', 'Меню'],\
                           'auto_alert_info': ['Меню'],\
                           'auto_alert_drop': ['Подтвердить'],\
                           'auto_alert_not_exist': ['Включить оповещение о своём городе', 'Включить оповещение о выбранном городе', 'Меню'],\
                           'today/time_auto': ['Вывести погоду на один день', 'Вывести погоду для нескольких дней', 'Меню'],\
                           'weather_result_auto': ['Меню'],\
                           'interval_auto':['Меню', 'input'],\
                           'city_search_auto': ['Меню', 'input'],\
                           'time_of_first_auto': ['Меню', 'input'],\
                           'time_auto_choice': ['Меню', 'input'],\
                           'auto_alert_confirm': ['Подтвердить']}


    def __init__(self, id: int, user_data):
        self.city_default = ''

        for i in user_data:
            self.user[i] = user_data[i]


    def close_session(self, user_data):
        for i in user_data:
            user_data[i] = self.user[i]


    def get_buttons(self):
        return self.all_interface_state[self.user['state']]


    def waiting_for_input(self):

        if self.user['state'] == 'main_menu':
            return False

        elif self.user['state'] == 'today/time_res':
            return False

        elif self.user['state'] == 'weather_result':
            return False

        elif self.user['state'] == 'city_search':
            return True

        elif self.user['state'] == 'time_res_choice':
            return True

        elif self.user['state'] == 'auto_alert_exist':
            return False

        elif self.user['state'] == 'auto_alert_info':
            return False

        elif self.user['state'] == 'auto_alert_drop':
            return False

        elif self.user['state'] == 'auto_alert_not_exist':
            return False

        elif self.user['state'] == 'today/time_auto':
            return False

        elif self.user['state'] == 'interval_auto':
            return True

        elif self.user['state'] == 'weather_result_auto':
            return True

        elif self.user['state'] == 'city_search_auto':
            return True

        elif self.user['state'] == 'time_of_first_auto':
            return True

        elif self.user['state'] == 'time_auto_choice':
            return True

        elif self.user['state'] == 'auto_alert_confirm':
            return False


    def button_handler(self, num: int, id):

        if self.user['state'] == 'main_menu':#меню
            if num == 0:
                if self.city_default == '':
                    self.logger.warning(('id%s ' %(str(self.user['id']))) + 'Попытка доступа к своему городу, который не указан в профиле')
                    self.user['state'] = 'city_search'
                else:
                    self.logger.info(('id%s ' %(str(self.user['id']))) + 'Выбор своего города для получения погоды - ' + self.city_default)
                    self.user['state'] = 'today/time_res'
            elif num == 1:
                    self.logger.info(('id%s ' %(str(self.user['id']))) + 'Выбор ввода города для получения погоды')
                    self.user['state'] = 'city_search'
            elif num == 2:
                if self.user['auto_warn']:
                    self.logger.info(('id%s ' %(str(self.user['id']))) + 'Переход к настройкам автооповещения')
                    self.user['state'] = 'auto_alert_exist'
                else:
                    self.logger.info(('id%s ' %(str(self.user['id']))) + 'Переход к созданию автооповещения')
                    self.user['state'] = 'auto_alert_not_exist'

        elif self.user['state'] == 'today/time_res':#выбор 1 день или несколько - одноразовый
            if num == 0:
                self.user['days'] = 1
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Переход к выводу погоды на ' + str(self.user['days']) + ' дней в городе ' + self.user['city'])
                self.user['state'] = 'weather_result'
            elif num == 1:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Выбор ввода количества дней')
                self.user['state'] = 'time_res_choice'
            elif num == 2:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Возврат в меню')
                self.user['state'] = 'main_menu'

        elif self.user['state'] == 'weather_result':#вывод погоды одноразовый
            if num == 0:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Возврат в меню')
                self.user['state'] = 'main_menu'

        elif self.user['state'] == 'city_search':#выбор города - одноразовый
            if num == 0:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Возврат в меню')
                self.user['state'] = 'main_menu'

        elif self.user['state'] == 'time_res_choice':#выбор колличество дней для вывода - одноразовый
            if num == 0:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Возврат в меню')
                self.user['state'] = 'main_menu'

        elif self.user['state'] == 'auto_alert_exist':#если автооповещение уже есть
            if num == 0:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Получение информации по состоянию автооповещения')
                self.user['state'] = 'auto_alert_info'
            elif num == 1:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Удаление подключённого автооповещения')
                self.user['state'] = 'auto_alert_drop'
            elif num == 2:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Возврат в меню')
                self.user['state'] = 'main_menu'

        elif self.user['state'] == 'auto_alert_info':#вывод информации по автооповещению
            if num == 0:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Возврат в меню')
                self.user['state'] = 'main_menu'

        elif self.user['state'] == 'auto_alert_drop':#отключение автооповещения
            self.user['auto_warn'] = False
            if num == 0:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Возврат в меню')
                self.user['state'] = 'main_menu'

        elif self.user['state'] == 'auto_alert_not_exist':#если автооповещения нет
            if num == 0:
                if self.city_default == '':
                    self.logger.warning(('id%s ' %(str(self.user['id']))) + 'Попытка доступа к совему городу, который не указан в профиле')
                    self.user['state'] = 'city_search_auto'
                else:
                    self.logger.info(('id%s ' %(str(self.user['id']))) + 'Выбор своего города для получения автооповещения')
                    self.user['state'] = 'today/time_auto'
            elif num == 1:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Выбор ввода города для получения автооповещения')
                self.user['state'] = 'city_search_auto'
            elif num == 2:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Возврат в меню')
                self.user['state'] = 'main_menu'

        elif self.user['state'] == 'today/time_auto':#выбор 1 день или несколько - автооповещение
            if num == 0:
                self.user['days_auto'] = 1
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Выбор автооповещения на ' + str(self.user['days_auto']) + ' дней')
                self.user['state'] = 'time_of_first_auto'
            elif num == 1:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Выбор ввода количества дней для автооповещения')
                self.user['state'] = 'interval_auto'
            elif num == 2:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Веозврат в меню')
                self.user['state'] = 'main_menu'

        elif self.user['state'] == 'interval_auto':#выбор колличество дней для вывода - автооповещение
            if num == 0:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Возврат в меню')
                self.user['state'] = 'main_menu'

        elif self.user['state'] == 'weather_result_auto':#вывод погоды - автооповещение
            if num == 0:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Возврат в меню')
                self.user['state'] = 'main_menu'

        elif self.user['state'] == 'city_search_auto':#выбор города - автооповещение
            if num == 0:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Возврат в меню')
                self.user['state'] = 'main_menu'

        elif self.user['state'] == 'time_of_first_auto':#выбор времени - автооповещение
            if num == 0:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Возврат в меню')
                self.user['state'] = 'main_menu'

        elif self.user['state'] == 'time_auto_choice':#выбор цикла - автооповещение
            self.user['auto_warn'] = True
            if num == 0:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Возврат в меню')
                self.user['state'] = 'main_menu'

        elif self.user['state'] == 'auto_alert_confirm':#подтверждение автооповещения
            if num == 0:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Возврат в меню')
                self.user['state'] = 'main_menu'



    def input_handler(self, text: str, id):

        if self.user['state'] == 'city_search':#выбор города - одноразовый
            self.user['city'] = text
            self.logger.info(('id%s ' %(str(self.user['id']))) + 'Выбор города ' + text + ' для получения погоды')
            self.user['state'] = 'today/time_res'
            try:
                num = int(text)
                self.logger.warning(('id%s ' %(str(self.user['id']))) + 'Неправильный ввод города')
            except:
                num = 0

        elif self.user['state'] == 'time_res_choice':#выбор колличество дней для вывода - одноразовый
            try:
                self.user['days'] = int(text)
                if self.user['days'] > 9 or self.user['days'] < 0:
                    self.logger.warning(('id%s ' %(str(self.user['id']))) + 'Неправильное значение колличества дней')
                    raise ValueError('Wrong value')
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Переход к выводу погоды на ' + str(self.user['days']) + ' дней в городе ' + self.user['city'])
                self.user['state'] = 'weather_result'
            except ValueError as err:
                self.logger.error(('id%s ' %(str(self.user['id']))) + 'Не числовое значение в выборе дней')
                print(err)

        elif self.user['state'] == 'interval_auto':#выбор колличество дней для вывода - автооповещение
            try:
                self.user['days_auto'] = int(text)
                if self.user['days_auto'] > 9 or self.user['time_auto'] < 0:
                    self.logger.warning(('id%s ' %(str(self.user['id']))) + 'Неправильное значение колличества дней для автооповещения')
                    raise ValueError('Wrong value')
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Автооповещение на ' + str(self.user['days_auto']) + ' дней')
                self.user['state'] = 'time_of_first_auto'
            except ValueError as err:
                self.logger.error(('id%s ' %(str(self.user['id']))) + 'Не числовое значение в выборе цикла')
                print(err)



        elif self.user['state'] == 'city_search_auto':#выбор города - автооповещение
            self.user['city_auto'] = text
            self.logger.info(('id%s ' %(str(self.user['id']))) + 'Выбор города ' + text + ' для автооповещения')
            self.user['state'] = 'today/time_auto'
            try:
                num = int(text)
                self.logger.warning(('id%s ' %(str(self.user['id']))) + 'Неправильный ввод города для автооповещения')
            except:
                num = 0

        elif self.user['state'] == 'time_of_first_auto':#выбор времени - автооповещение
            try:
                alert_time = datetime.datetime.strptime(text, '%H:%M')
                alert_time = datetime.datetime.now().replace(hour=alert_time.hour, minute=alert_time.minute, second=0)

                self.user['first_time_auto'] = alert_time
                self.logger.info(('id%s ' % (str(self.user['id']))) + 'Выбор времени ' + (
                        '%d:%d' % (alert_time.hour, alert_time.minute)) + ' первого автооповещения')
                self.user['state'] = 'time_auto_choice'
            except:
                self.logger.error(('id%s ' %(str(self.user['id']))) + 'Неверное значение в выборе первого оповещения')


        elif self.user['state'] == 'time_auto_choice':#выбор цикла - автооповещение
            try:
                self.user['time_auto'] = int(text)
                if self.user['time_auto'] < 1:
                    self.logger.error(('id%s ' %(str(self.user['id']))) + 'Неверное числовое значение в выборе цикла')
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Выбор цикла в ' + str(self.user['time_auto']) + ' дней для автооповещения')
                self.user['state'] = 'auto_alert_confirm'
                self.user['auto_warn'] = True
            except:
                self.logger.error(('id%s ' %(str(self.user['id']))) + 'Не числовое значение в выборе цикла')


    def auto(self):
        self.user['state'] = 'weather_result_auto'


    def get_msg(self):

        if self.user['state'] == 'main_menu':
            return 'Меню'

        elif self.user['state'] == 'today/time_res':
            return 'Погода только на один день?'

        elif self.user['state'] == 'weather_result':
            weather = get_weather(self.user['city'], self.user['days'])
            if len(weather) != 0:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Вывод погоды на ' + str(self.user['days']) + ' дней в городе ' + self.user['city'])
                return weather
            else:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Не сайте не найден город ' + self.user['city'])
                return 'Ошибка - не найден город'

        elif self.user['state'] == 'city_search':
            return 'Введите город'

        elif self.user['state'] == 'time_res_choice':
            return 'Введите колличество дней в пределах 9'

        elif self.user['state'] == 'auto_alert_exist':
            return 'Автоматическое оповещение задано'

        elif self.user['state'] == 'auto_alert_info':
            return 'Город подключённый к оповещению - ' + self.user['city_auto'] + '\nСледующее оповещение - '\
                + self.user['first_time_auto'].strftime('%d.%m.%Y - %H:%M') + '\nПериод оповещения - ' + str(self.user['time_auto']) +\
                '\nКолличество дней в оповещении - ' + str(self.user['days_auto'])

        elif self.user['state'] == 'auto_alert_drop':
            return 'Автоматическое оповещение будет отменено'

        elif self.user['state'] == 'auto_alert_not_exist':
            return 'Автоматическое оповещение ещё не настроено'

        elif self.user['state'] == 'today/time_auto':
            return 'Погода только на один день?'

        elif self.user['state'] == 'interval_auto':
            return 'Ведите колличество дней'

        elif self.user['state'] == 'weather_result_auto':
            weather = get_weather(self.user['city_auto'], self.user['days_auto'])
            if len(weather) != 0:
                self.logger.info(('id%s ' %(str(self.user['id']))) + ('Вывод погоды на %s дней в городе %s с циклом %s'\
                    %(str(self.user['days_auto']), str(self.user['city_auto']), str(self.user['time_auto']))))
                self.user['state'] = 'main_menu'
                return weather
            else:
                self.logger.info(('id%s ' %(str(self.user['id']))) + 'Не сайте не найден город ' + self.user['city_auto'])
                self.user['state'] = 'main_menu'
                return 'Ошибка - не найден город'

        elif self.user['state'] == 'city_search_auto':
            return 'Введите город для подключения автооповещения'

        elif self.user['state'] == 'time_of_first_auto':
            return 'Введите время первого автоматического оповещения в формате 13:37'

        elif self.user['state'] == 'time_auto_choice':
            return 'Введиите период автоматического оповещения в днях - число больше 0'

        elif self.user['state'] == 'auto_alert_confirm':
            return 'Автоматическое оповещение будет включено'