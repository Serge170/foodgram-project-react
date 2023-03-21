### Проект Foodgram

**Foodgram** - продуктовый помощник.

[![Django-app workflow](https://github.com/serge170/foodgram-project-react/actions/workflows/main.yml/badge.svg)](https://github.com/Serge170/foodgram-project-react/actions/workflows/main.yml)

Пользователи **Foodgram** могут публиковать рецепты (**Recipes**), подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать в формате .txt сводный список продуктов (**Ingredients**), необходимых для приготовления одного или нескольких выбранных блюд.

Для удобства навигации по сайту рецепты размечены тэгами (**Tags**)

### Инструкция для разворачивания проекта на удаленном сервере:

- Склонируйте проект из репозитория:

```sh
$ git clone https://github.com/Serge170/foodgram-project-react.git
```

- Выполните вход на удаленный сервер

- Подготовьте и установите DOCKER на сервер:
```sh
sudo apt update
sudo apt install docker.io 
```

- Установитe docker-compose на сервер:
```sh
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

- Отредактируйте конфигурацию сервера NGNIX:
```sh
Локально измените файл ..infra/nginx.conf - замените данные в строке server_name на IP-адрес удаленного сервера
```

- Скопируйте файлы docker-compose.yml и nginx.conf из директории ../infra/, а также папку docs из головной директории на удаленный сервер:
```sh
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
scp .env <username>@<host>:/home/<username>/.env
scp -r docs <username>@<host>:/home/<username>/docs
```
- Создайте переменные окружения (указаны в файле ../infra/env.example) и добавьте их в Secrets GitHub Actions

- Установите и активируйте виртуальное окружение:

```sh
python -m venv venv 
source venv/Scripts/activate
python -m pip install --upgrade pip
``` 

- Запустите приложение в контейнерах:

```sh
sudo docker-compose up -d --build
```

- Выполните миграции:

```sh
sudo docker-compose exec backend python manage.py migrate
```

- Создайте суперпользователя:

```sh
sudo docker-compose exec backend python manage.py createsuperuser
```

- Выполните команду для сбора статики:

```sh
sudo docker-compose exec backend python manage.py collectstatic --no-input
```

- Команда для заполнения тестовыми ингридиентами:
```sh
sudo docker-compose exec backend python manage.py import_db
```

- Команда для остановки приложения в контейнерах:

```sh
sudo docker-compose down -v
```

### Для запуска на локальной машине:

- Склонируйте проект из репозитория:

```sh
$ git clone https://github.com/Serge170/foodgram-project-react.git
```

- В папке ../infra/ переименуйте файл example.env в .env и заполните своими данными:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=<...> # секретный ключ django-проекта из settings.py
```
***

Проект развернут по IP [51.250.79.106](http://51.250.79.106/)

Доступ в админ-панель:

```sh
http://51.250.79.106/admin
login: admim@mail.ru
pass: admin
```

### Автор

Сергей Елисеев
