# smart_wifi

## Запуск
* Скопировать `.env.example` в `.env` и отредактировать настройки
* Запустить `docker-compose up -d`
* Создать суперпользователя `docker-compose exec web python3 manage.py createsuperuser`
* Создать миграцию `docker-compose exec web python3 manage.py makemigrations`
* Выполнить миграцию `docker-compose exec web python3 manage.py migrate`
