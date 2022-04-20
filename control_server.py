from flask import Flask, request
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


COMMANDS = ['start', 'autoset', 'assistant', 
            'stop', 'set', 'get', 'status', 'track']
api_key = 'c745cc1883a84f9bbe3252d865009a52'
erudite_url = 'https://nvr.miem.hse.ru/api/erudite/'
erudite_headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "key": api_key
 }
running = True

app = Flask(__name__)


@app.route('/', methods=['POST'])
def server():
    if request.method == 'POST':
        data = request.get_json(force=True)
        try:
            if(data['command'] in COMMANDS):
                try:
                    # Запрос к базе данных erudite
                    device = get(erudite_url + 'equipment?room_name='
                                + data['room_name'] + '&type=Tracker',
                                headers=erudite_headers).json()
                    if(type(device) is dict):
                        return error('The tracker is not set on provided room',
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
                        return answer('OK', response.json()['information'])
                    else:
                        return error(response.json()['description'],
                                    ServerError.TrackerError)
                except ConnectionError:
                    return error('No connection to tracker device', ServerError.TrackerError)
                except JSONDecodeError:
                    return error('Unknown Error', ServerError.TrackerError)
            else:
                return error('Command doesnt exist',
                             ServerError.InvalidCommand)
        except KeyError:
            return error('Data format is incorrect',
                         ServerError.NoCommandProvided)

# Функция для возврата ошибки
def error(desc, code):
    return dumps({
        'status': 'Error',
        'code': str(code),
        'description': desc
    }), 400


# Функция для возврата ответа от сервера
def answer(type, data=None):
    return dumps({
        'status': type,
        'information': data
    }), 200

# Поток для чтения и отправки логов
def status_thread():
    log = {}
    response = get(erudite_url + 'equipment?type=Tracker',
                   headers=erudite_headers)
    trackers = response.json()
    for tracker in trackers:
        log[tracker['name']] = {}
    today = date.today()
    start_time = datetime(today.year, today.month, today.day, 9, 30)
    end_time = datetime(today.year, today.month, today.day, 21)
    while trackers is not None and running:
        try:
            time = datetime.now()
            if((time.minute) % 15 == 0 and time.second == 0
                and time >= start_time and time <= end_time):
                for tracker in trackers:
                    try:
                        log_response = post('http://' + tracker['ip'] + ':' +
                                        str(tracker['port']) + '/track',
                                        data=dumps({'command':'log'}))
                        data = log_response.json()
                        if(data['status'] == 'Error' or data['information']['log'] is None):
                            continue
                        time = time.replace(second=0)
                        log[tracker['name']][time.strftime('%Y-%m-%d %H:%M:%S')] = data['information']['log']
                        if(len(log[tracker['name']]) > 4):
                            del log[tracker['name']][list(log[tracker['name']].keys())[0]]
                        room_name = tracker['room_name']
                        from_date = time.replace(hour=time.hour - 1)
                        to_date = time
                        camera_response = get(erudite_url + 'equipment?room_name=' +
                                    room_name,
                                    headers=erudite_headers).json()
                        cam = None
                        for camera in camera_response:
                            if(camera['role'] == 'main'):
                                cam = camera
                                break
                        if(cam is not None):
                            records_response = get(erudite_url + 'records?camera_ip=' +
                                                cam['ip'] + '&&fromdate=' +
                                                from_date.strftime('%Y-%m-%d %H:%M:%S') +
                                                '&&todate=' + to_date.strftime('%Y-%m-%d %H:%M:%S'),
                                                headers=erudite_headers).json()
                            for rec in records_response:
                                time_end = rec['end_point']
                                if('tracker_log' not in rec.keys() and time_end in list(log[tracker['name']].keys())):
                                    response = patch(erudite_url + 'records/' + rec['id'],
                                                    data=dumps({'tracker_log': log[tracker['name']][time_end]}),
                                                    headers=erudite_headers).json()
                                    del log[tracker['name']][time_end]
                    except ConnectionError:
                        print('No connection to the device') 
            if(date.today() != today):
                today = date.today()
                start_time = datetime(today.year, today.month, today.day, 9, 30)
                end_time = datetime(today.year, today.month, today.day, 21)
            sleep(1)
        except:
            print('Unknown error with status thread')


if __name__ == '__main__':
    thread = Thread(target=status_thread, name="status_thread")
    thread.start()
    app.run(host='0.0.0.0')
    running = False
