## 🔧 Скачивание проекта и подготовка к запуску

### Клонирование репозитория
Выполните в терминале:

Через SSH (рекомендуется)
```bash
git clone git@github.com:SaitBakhteev/sprintProject.git
```
Или через HTTPS
```bash
git clone https://github.com/SaitBakhteev/sprintProject.git
```
Перейдите в директория проекта
```bash
cd sprintProject
```

### Создание виртуального окружения

```bash
python -m venv venv
```

#### Активация окружения
Windows:
```bash
venv\Scripts\activate
```
Linux/Mac:
```bash
source venv/bin/activate
```
#### Настройка и установка зависимостей

**❗️КРИТИЧЕЧКИ ВАЖНО ❗️** <br> 
*Файл requirements.txt у вас должен выглядеть*:
- для [первого](#способ-1-режим-разработчика) способа запуска:
```python
#psycopg2-binary==2.9.10
psycopg2==2.9.10
```
- для [второго](#-способ-2-сборка-docker-образа-и-запуск-контейнера) способа запуска:
```python
psycopg2-binary==2.9.10
#psycopg2==2.9.10
```

```bash
pip install -r requirements.txt
```

### Настройка ключевых параметров в файле окружения
В файле .env нужно прописать значения для следующих переменных:
```ini
SECRET_KEY=<>

# данные для подключения к PostgreSQL
FSTR_DB_HOST=<>
FSTR_DB_PORT=<>
FSTR_DB_LOGIN=<>
FSTR_DB_PASS=<>
FSTR_DB_NAME=<>
```

# 🔑 Запуск проекта двумя способами
## Способ 1 (режим разработчика)
- ### Запустите через терминал сервер командой:
```bash
python manage.py runserver
```
## 🐳 Способ 2 (Сборка docker образа и запуск контейнера)
выполните последовательно следующие команды 
```bash
docker build -t django-app .
docker run -p 8000:8000 django-app
```
# 🚀 Работа с API
- ### Перейдите в браузере на страницу http://localhost:8000/api/docs.
- ### Откройте эндпоинт `/pereval/`, введите данные в теле запроса и запустите.

⚠️ ЗАМЕЧАНИЯ ПО API
- #### В ТЗ прописано применение API как сервера мобильного приложения. Поэтому в `data` передаем изображение как строку base64 в таком формате   

```json

  "images": [
  {
  "data": "data:image/jpeg;base64,/<строка base64>"
  }
]
```

- #### Если API получает пользователя с email, отсутствующим в БД, то он автоматически создает в БД нового пользователя



