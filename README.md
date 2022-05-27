# Tracker Control Server
Для возможности удаленного управления трекерами в разных аудиториях необходимо установить управляющий сервер, работающий с собственной базой данных MySQL. Для работы управляющего сервера необходимо добавить соответствующие записи о трекерах в базу данных.
1. Загрузите репозиторий с сервером

`git clone https://git.miem.hse.ru/592/ptz-tracker.git -b ControlServer server`

2. Перейдите в директорию  сервера

`cd server`
- Запуск сервера

`docker-compose up -d --remove-orphans --build`
- Остановка сервера

`docker-compose down --remove-orphans`

- Просмотр логов

`docker logs --tail 50 --follow --timestamps p592-python`
