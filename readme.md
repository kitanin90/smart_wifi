# smart_wifi

# I. Загрузка проекта на сервер
1. Загрузить проект на ПК через терминал можно с помощью команды:
```sh
$ git clone https://github.com/kitanin90/smart_wifi.git
```

# II. Настройка проекта
После успешной загрузки необходимо провести ряд настроек:
* Скопировать `.env.example` в `.env` и отредактировать файл(Либо просто переименовать файл)
* Изменить настройки в `settings.py`
* Запустить `docker-compose up -d`
* Создать суперпользователя `docker-compose exec web python3 manage.py createsuperuser`
* Создать миграцию `docker-compose exec web python3 manage.py makemigrations`
* Выполнить миграцию `docker-compose exec web python3 manage.py migrate`


# III. Настройка административной панели Django
В случае успешного выполнения пунктов, описанных выше Вы сможете зайти в админ.панель Django в браузере перейдя по `localhost/admin`

## Добавление Корпусов и Факультетов
* Прежде всего добавьте корпуса в соответствующем разделе.
Заполните пункты: `Название` и `адрес`

* Аналогично добавьте факультеты

## Создание клиентов:
***Ручное добавление:***
* Добавить новых клиентов можно в разделе `Клиенты`
* Заполнить соответствующие поля: ФИО, Username, Статус, Телефон, Факультет
* `Username` клиента состоит из его фамилии и инициалов (например, IvanovAA)

Чтобы задать пароль для клиента, перейдите и добавьте в `Параметры клиента`:
1. Заполните соответствующий `Username` клиента
2. В `Attribute` введите `Cleartext-Password`
3. `Op` будет содержать `:=`
4. В `Value` введите пароль для клиента

***Автоматическое добавление:***

Если у вас большая база клиентов, вы можете добавить их с помощью файла в формате `.csv`. Для этого перейдите в браузере на `http://localhost/panel/upload_file`.
В данном случае, скрипт создаст и настроит параметры клиента вместо вас.

**Внимание!** 
Скрипт начинает считывать клиентов с 7 строки в вашей базе данных! Каждый параметр разделяется с помощью `;` в соответствующей колонки(Пример формата для заполнения БД: `;;ИвановАА;;;;Пароль;`)


## Настройка точек доступа
Для системы нужно знать с какими роутерами ей нужно работать.
Подключитесь к роутеру через сетевой кабель по ssh и введите пароль от админ.панели роутера(например, ssh root@10.42.0.46). С помощью команды `ifconfig`
Для этого необходимо каждый роутер добавить в разделе `Роутеры`:
Некоторые данные можно узнать с помощью `ifconfig` 
 * `Название`  - название роутрера
 * `ip`  - Ip-адрес узнайте в `ifconfig` 
 * `Порт`  - Обычно "0"
 * `Токен`  - Токен узнайте `ifconfig` (например, serkettoken)
 * `MAC`  - MAC узнайте в `ifconfig` (например, 1C-2S-3X-4Z-5T-6J)
 * `Корпус`  - Выберите корпус, в котором стоит роутер

**ВНИМАНИЕ!** После изменений в админ.панели Django перезагрузите freeradius командой `docker-compose restart freeradius`


# IV. Ошибки и способы устранения

# `NAS matching query does not exist` 
Ошибка подразумевает пустое значение или неправильное заполнение MAC-адреса у роутера в панели управления Django.
Проверьте правильность введеных данных по пункту `Настройка точек доступа`
***ВНИМАНИЕ!*** MAC-адрес записывается через "-", а не двоеточие
