# Badminton (Quasar App + FastAPI)

## Что должно быть установлено на новом устройстве

Проверка:
```
git --version
node -v
npm -v
```

### Скопировать ссылку на репозиторий

Это ссылка: https://github.com/the-punkin/badminton

### Клонировать репозиторий

В терминале на новом устройстве:

```
git clone https://github.com/the-punkin/badminton
```

Если нужно клонировать другую ветку (не main):

```
git clone -b имя_ветки --single-branch https://github.com/ссылка на репозиторий
```

Например,

```
git clone -b update --single-branch https://github.com/the-punkin/badminton
```

Что происходит:

* создаётся папка badminton
* в неё загружается весь код и история
* node_modules НЕ загружается (и это правильно)

Перейти в проект:
```
cd badminton
```

### Установить зависимости

```
npm install
```
Команда:
* читает package.json
* скачивает node_modules
* воссоздаёт окружение

### Запуск сервера

Перейти в папку /test, где содержится файл server.py
```
cd test
```

Для запуска сервера:
Либо:
```
uvicorn server:app --reload
```
Либо:
```
uvicorn server:app --host 0.0.0.0 --port 8000 --reload
```
Второй говорит серверу прослушивать все сетевые интерфейсы, а первый только localhost.

### Заупск клиента

Для запуска клиента:
```
quasar dev
```

## После этого в браузере откроется Quasar App, где видео загружается и выводится на страрницу.