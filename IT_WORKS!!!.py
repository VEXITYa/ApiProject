from flask import Flask, request
import logging
import json
import requests
from hashlib import sha1
import random


HEADERS = {
    'user-agent': 'pypi.org/project/haveibeenpwnd/ v0.1',
    'api-version': 2
    }

range_url = 'https://api.pwnedpasswords.com/range/{}'

functions_that_work_good = [
    'joke - случайная шутка',
    'bitcoin rate - курс биткоина'
    ]

functions_that_work_worst = [
    'rand name - случайное имя (~)',
    'rand advice - случайный совет (~)',
    'check day - проверка на праздник (~)',
    'check pass {pass} - проверка пароля по базам (~)',
    'donald - случайные фразы Трампа о других (~)',
    'news - горячие новости'
    ]

functions_that_work_worst = sorted(functions_that_work_worst)
functions_that_work_good = sorted(functions_that_work_good)


def check_password(password):
    hashed_password = sha1(password.encode('utf-8')).hexdigest()

    prefix = hashed_password[:5]
    suffix = hashed_password[5:]

    # only send a prefix of 5 chars to haveibeenpwnd.com
    response = requests.get(range_url.format(prefix), HEADERS).text

    for line in iter(response.splitlines()):
        hex, _, count = line.partition(':')
        if hex == suffix.upper():
            return int(count)
    else:
        return 0


while True:
    text = input()
    if 'rand name' in text.lower():
        response = requests.get("https://uinames.com/api/?region=russia")
        todos = json.loads(response.text)
        print(todos['name'])

    elif 'rand advice' in text.lower():
        response = requests.get("https://api.adviceslip.com/advice")
        todos = json.loads(response.text)
        print(todos['slip']['advice'])

    elif 'check day' in text.lower():
        response = requests.get("https://datazen.katren.ru/calendar/day/")
        todos = json.loads(response.text)

        if todos['holiday']:
            print('Сегодня праздник.')

        else:
            print('Сегодня не праздник.')

    elif 'check pass' in text.lower():
        tmp = text.split()[-1]
        k = check_password(tmp)

        if k == 0:
            print("Очень хорошо, я не нашла твоего пароля в базах. Но ты все равно будь аккуратен.".format(k))

        elif k <= 100:
            print("Я нашла твой пароль в базах {} раз, это в принципе нормально, но я рекомендую тебе сменить пароль".format(k))

        elif k > 100:
                print("Я нашла твой пароль в базах {} раз, я рекомендую тебе сменить пароль.".format(k))

    elif 'donald' in text.lower():
        response = requests.get("https://api.tronalddump.io/random/quote")
        todos = json.loads(response.text)
        print('Donald Trump about {}.\n{}'.format(todos['tags'][0], todos['value']))
        print('высказывание в Twitter:', str(todos["_embedded"]["source"][0]["url"]))

    elif 'news' in text.lower():
            url = ('https://newsapi.org/v2/top-headlines?'
                   'country=ru&'
                   'apiKey=2412173a48da404d8e4088f2c8bc05be')

            response = requests.get(url)
            d = response.json()
            x = random.randint(0, len(d['articles']))

            print(d['articles'][x]['title'])
            print('Источник' + " " + d['articles'][x]['url'])

    elif 'команды' in text.lower():
        tmp = ''
        print('В нашем "проекте" мы реализовали следующие команды:')
        for i in range(len(functions_that_work_good)):
            tmp += '\n' + functions_that_work_good[i]

        tmp += '\n' + '~' * 39

        for i in range(len(functions_that_work_worst)):
            tmp += '\n' + functions_that_work_worst[i]

        print(tmp)

    else:
        print('Такой команды не существует.')
