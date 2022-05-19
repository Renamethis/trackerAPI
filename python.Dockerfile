# Dockerfile02-python-program
# Родительский образ
FROM python:3.6.9-slim

# Устанавливаем обновления, загружаем необходимые программы
RUN apt-get update -y \
    && apt-get install -y openvpn nano htop iputils-ping

# Обновляем pip
RUN pip install -U pip 

# Устанавливаем библиотеки
RUN pip3 install flask jsonify requests flask_sqlalchemy pymysql
