from flask import Flask, request
import logging
import json
import requests
from hashlib import sha1
import random

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)


sessionStorage = {}

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
    'news - горячие новости (~)'
    ]

functions_that_work_worst = sorted(functions_that_work_worst)
functions_that_work_good = sorted(functions_that_work_good)


@app.route('/post', methods=['POST'])
def main():
    logging.info('Request: %r', request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(response, request.json)
    logging.info('Response: %r', response)
    return json.dumps(response)


def handle_dialog(res, req):
    user_id = req['session']['user_id']

    if req['session']['new']:
        res['response']['buttons'] = [
                {
                    'title': 'Команды',
                    'hide': True
                }
            ]
        res['response']['text'] = 'Привет! Назови своё имя!'
        sessionStorage[user_id] = {
            'first_name': None,  # здесь будет храниться имя
            'game_started': False  # здесь информация о том, что пользователь начал игру. По умолчанию False
        }
        return

    if 'команды' in req['request']['nlu']['tokens']:
        res['response']['text'] = 'В нашем "проекте" мы реализовали следующие команды:'
        for i in range(len(functions_that_work_good)):
            res['response']['text'] += '\n' + functions_that_work_good[i]

        res['response']['text'] += '\n' + '#' * 20

        for i in range(len(functions_that_work_worst)):
            res['response']['text'] += '\n' + functions_that_work_worst[i]

        return


    elif sessionStorage[user_id]['first_name'] is None:
        first_name = get_first_name(req)

        if first_name is None:
            res['response']['text'] = 'Не расслышала имя. Повтори, пожалуйста!'
            res['response']['buttons'] = [
                {
                    'title': 'Команды',
                    'hide': True
                }
            ]


        else:
            sessionStorage[user_id]['first_name'] = first_name
            # создаём пустой массив, в который будем записывать города, которые пользователь уже отгадал
            sessionStorage[user_id]['guessed_cities'] = []
            # как видно из предыдущего навыка, сюда мы попали, потому что пользователь написал своем имя.
            # Предлагаем ему сыграть и два варианта ответа "Да" и "Нет".
            res['response']['text'] = f'Приятно познакомиться, {first_name.title()}.'
            res['response']['buttons'] = [
                {
                    'title': 'Команды',
                    'hide': True
                }
            ]


    else:
        res['response']['text'] = "Такой команды не существует."
        res['response']['buttons'] = [
                {
                    'title': 'Команды',
                    'hide': True
                }
            ]


    if 'joke' in req['request']['command'].lower():
        response = requests.get("https://icanhazdadjoke.com/slack")
        todos = json.loads(response.text)
        res['response']['text'] = todos['attachments'][0]['fallback']
        res['response']['buttons'] = [
                {
                    'title': 'Команды',
                    'hide': True
                }
            ]


    elif 'rand name' in req['request']['command'].lower():
        response = requests.get("https://uinames.com/api/?region=russia")
        todos = json.loads(response.text)
        res['response']['text'] = todos['name']
        res['response']['buttons'] = [
                {
                    'title': 'Команды',
                    'hide': True
                }
            ]


    elif 'rand advice' in req['request']['command'].lower():
        response = requests.get("https://api.adviceslip.com/advice")
        todos = json.loads(response.text)
        res['response']['text'] = todos['slip']['advice']
        res['response']['buttons'] = [
                {
                    'title': 'Команды',
                    'hide': True
                }
            ]


    elif 'check day' in req['request']['command'].lower():
        response = requests.get("https://datazen.katren.ru/calendar/day/")
        todos = json.loads(response.text)

        if todos['holiday']:
            res['response']['text'] = 'Сегодня праздник.'

        else:
            res['response']['text'] = 'Сегодня не праздник.'
        res['response']['buttons'] = [
                {
                    'title': 'Команды',
                    'hide': True
                }
            ]


    elif 'bitcoin rate' in req['request']['command'].lower():
        response = requests.get("https://api.cryptonator.com/api/ticker/btc-usd")
        todos = json.loads(response.text)
        res['response']['text'] = '1 BTC = {} USD'.format(str(todos['ticker']['price']))
        res['response']['buttons'] = [
                {
                    'title': 'Команды',
                    'hide': True
                }
            ]


    elif 'check pass' in req['request']['command'].lower():
        k = check_password(req['request']['command'].split()[-1])

        if k == 0:
            res['response']['text'] = "Очень хорошо, я не нашла твоего пароля в базах. Но ты все равно будь аккуратен.".format(k)

        elif k <= 100:
            res['response']['text'] = "Я нашла твой пароль в базах {} раз, это в принципе нормально, но я рекомендую тебе сменить пароль".format(k)

        elif k > 100:
            res['response']['text'] = "Я нашла твой пароль в базах {} раз, я рекомендую тебе сменить пароль.".format(k)
        res['response']['buttons'] = [
                {
                    'title': 'Команды',
                    'hide': True
                }
            ]


    elif 'donald' in req['request']['command'].lower():
        response = requests.get("https://api.tronalddump.io/random/quote")
        todos = json.loads(response.text)
        res['response']['text'] = 'Donald Trump about {}.\n{}'.format(todos['tags'][0], todos['value'])
        res['response']['buttons'] = [
                {
                    'title' : 'Команды',
                    'hide' : True
                },
                {
                    'title' : 'Показать высказывание в Twitter',
                    'hide' : True,
                    'url' : todos["_embedded"]["source"]["url"]
                }
            ]



    elif 'news' in req['request']['command'].lower():
        url = ('https://newsapi.org/v2/top-headlines?'
               'country=us&'
               'apiKey=2412173a48da404d8e4088f2c8bc05be')

        response = requests.get(url)
        d = response.json()
        x = random.randint(0, len(d['articles']))

        res['response']['text'] = d['articles'][x]['title']
        res['response']['buttons'] = [
                {
                    'title' : 'Команды',
                    'hide' : True
                },
                {
                    'title' : 'Источник',
                    'hide' : True,
                    'url' : d['articles'][x]['url']
                }
            ]


def get_first_name(req):
    # перебираем сущности
    for entity in req['request']['nlu']['entities']:
        # находим сущность с типом 'YANDEX.FIO'

        if entity['type'] == 'YANDEX.FIO':
            # Если есть сущность с ключом 'first_name', то возвращаем её значение.
            # Во всех остальных случаях возвращаем None.
            return entity['value'].get('first_name', None)


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


if __name__ == '__main__':
    app.run()