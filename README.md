# Foodgram
[![Github CI/CD](https://github.com/lllleeenna/foodgram-project-react/actions/workflows/foodgram_workflow/badge.svg)](https://github.com/lllleeenna/foodgram-project-react/actions)

«Продуктовый помощник»: сайт, на котором пользователи будут публиковать 
рецепты, добавлять чужие рецепты в избранное и подписываться на публикации 
других авторов. 
Сервис «Список покупок» позволит пользователям создавать список продуктов, 
которые нужно купить для приготовления выбранных блюд. 

### Технологии:
- Python 3.9
- Django 3.2
- djangorestframework 3.12.4
- nginx
- gunicorn
- docker-compose
- workflow

### Запуск проекта
Отредактируйте файл nginx.conf, в строке server_name впишите ip сервера.
Скопируйте файлы docker-compose.yaml и nginx.conf из проекта на сервер в 
/home/username/docker-compose.yaml и /home/username/nginx.conf
```
scp docker-compose.yaml <username>@<host>/home/<username>/docker-compose.yaml
scp nginx.conf <username>@<host>/home/<username>/nginx.conf
```
Скопируйте папку docs/ с документацией redoc из проекта на сервер в /home/username/

В репозитории на Github добавьте данные в Settings - Secrets - Actions secrets:
```
DOCKER_USERNAME - имя пользователя DockerHub
DOCKER_PASSWORD - пароль пользователя DockerHub
HOST - ip-адрес сервера
USER - пользователь
SSH_KEY - приватный ssh-ключ (публичный должен быть на сервере)
PASSPHRASE - кодовая фраза для ssh-ключа
DB_ENGINE - django.db.backends.postgresql
DB_HOST - db
DB_PORT - 5432
DB_NAME - имя БД
POSTGRES_USER - пользователь БД
POSTGRES_PASSWORD - пароль для БД
SECRET_KEY - код для django
```
После деплоя на сервере

Выполнить миграции:
```
sudo docker-compose exec backend python manage.py migrate
```
Создайте суперпользователя:
```
sudo docker-compose exec backend python manage.py createsuperuser
```
Соберите статику:
```
sudo docker-compose exec backend python manage.py collectstatic --no-input
```
Загрузите ингредиенты:
```
sudo docker-compose exec backend python manage.py ingredients_load /app/ingredients.csv
```
### Адрес
http://51.250.90.189/

http://51.250.90.189/admin/

http://51.250.90.189/api/docs/

Логин: admin

Пароль: admin

