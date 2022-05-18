from flask import Flask, request
from flask.views import View
from json import dumps
from requests import post, get, patch
from requests.exceptions import ConnectionError
from json.decoder import JSONDecodeError
from enum import Enum, auto
from threading import Thread
from datetime import datetime, date
from time import sleep

class ServerError(Enum):
    InvalidCommand = auto()
    NoCommandProvided = auto()
    DeviceNotFound = auto()
    TrackerError = auto()

class Server(View):
    methods = ['GET', 'POST']
    COMMANDS = ['start', 'autoset', 'assistant', 
                'stop', 'set', 'get', 'status', 'track']
    api_key = 'c745cc1883a84f9bbe3252d865009a52'
    erudite_url = 'https://nvr.miem.hse.ru/api/erudite/'
    erudite_headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "key": api_key
    }
    def dispatch_request(self):
        if request.method == 'POST':
            data = request.get_json(force=True)
            try:
                if(data['command'] in self.COMMANDS):
                    try:
                        # Запрос к базе данных erudite
                        device = get(self.erudite_url + 'equipment?room_name='
                                    + data['room_name'] + '&type=Tracker',
                                    headers=self.erudite_headers).json()
                        if(type(device) is dict):
                            return self.error('The tracker is not set on provided room',
                                        ServerError.DeviceNotFound)
                        device = device[0]
                        device_ip = device['ip']
                        device_port = device['port']
                        # Передаем все параметры для команды set(если они есть)
                        body = {}
                        for key in data.keys():
                            if(key != 'room_name'):
                                body[key] = data[key]
                        # Отправляем запрос на необходимое устройство
                        response = post('http://' + device_ip + ':' +
                                        str(device_port) + '/track',
                                        data=dumps(body), timeout=20)
                        if(response.json()['status'] != 'Error'):
                            return self.answer('OK', response.json()['information'])
                        else:
                            return self.error(response.json()['description'],
                                        ServerError.TrackerError)
                    except ConnectionError:
                        return self.error('No connection to tracker device', ServerError.TrackerError)
                    except JSONDecodeError:
                        return self.error('Unknown Error', ServerError.TrackerError)
                else:
                    return self.error('Command doesnt exist',
                                ServerError.InvalidCommand)
            except KeyError:
                return self.error('Data format is incorrect',
                            ServerError.NoCommandProvided)
    # Функция для возврата ошибки
    def error(self, desc, code):
        return dumps({
            'status': 'Error',
            'code': str(code),
            'description': desc
        }), 400


    # Функция для возврата ответа от сервера
    def answer(self, type, data=None):
        return dumps({
            'status': type,
            'information': data
        }), 200