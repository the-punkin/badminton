# Badminton (Quasar App + FastAPI)

## Что должно быть установлено на новом устройстве

Проверка:

```
git --version
node -v
npm -v
```
Перед запуском необходимо также установить ffmpeg: https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-essentials.7z

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

### Настройка сервера

#### Делается один раз после клонирования репозитория!

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

```python -m venv venv``` - создается виртуальная среду.
```venv\Scripts\activate``` - запуск среды.
```pip install -r requirements.txt``` - установка зависимостей.

### Запуск сервера
Запустить виртуальную среду:
```
venv\Scripts\activate
```

Перейти в папку /test, где содержится файл server.py
```
cd test
```

Для запуска сервера.
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

### Важный момент:
Могут возникт ошибки/предпреждения такого вида:
```
FFmpeg not found. Please install ffmpeg.
Подтвердите действие на localhost:8081
Ошибка обработка: [WinError 2] Не удается найти указанный файл
```

Тогда нужно сделать следующее:
1. Убедиться, что ffmpeg у вас действительно скачан.
2. Зайти в переменные среды. Можно с помощью поиска: 

    ![alt text](image-2.png)

    Или с помощью сочетаний клавиш Win+R и написать systempropertiesadvanced:
    
    ![alt text](image-1.png)

3. Заходим в переменные среды:

    ![alt text](image-3.png)

4. Кликаем на Path: 

    ![alt text](image-4.png)

5. Нажимаем создать и вставляем путь до ffmpeg/bin (последний на скрине). Затем нажимаем "Ок" во всех окнах. 

    ![alt text](image-5.png)

После этого перезапустить сервер.