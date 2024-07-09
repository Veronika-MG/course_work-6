# Курсовая 6. Основы веб-разработки на Django

Разработка сервиса

Вы познакомились с основами Django и теперь можете выполнить серьезную задачу — создать 
сервис управления рассылками. Это первая часть курсовой работы, в которой вы закрепите 
полученные знания и научитесь применять их на практике. После выполнения этой части курсовой 
работы вы продолжите изучать Django, будете совершенствовать свой проект и добавлять новые 
функции.

1.	Реализуйте интерфейс заполнения рассылок, то есть CRUD-механизм для управления рассылками.
2.	Реализуйте скрипт рассылки, который работает как из командной строки, так и по расписанию.
3.	Добавьте настройки конфигурации для периодического запуска задачи при необходимости.

Сущности системы

- Клиент сервиса:
   - контактный email,
   - Ф. И. О.,
   - комментарий.
-Рассылка (настройки):
   - дата и время первой отправки рассылки;
   - периодичность: раз в день, раз в неделю, раз в месяц;
   - статус рассылки (например, завершена, создана, запущена).
- Сообщение для рассылки:
   - тема письма,
   - тело письма.
- Попытка рассылки:
   - дата и время последней попытки;
   - статус попытки (успешно / не успешно);
   - ответ почтового сервера, если он был.

Логика работы системы

•	После создания новой рассылки, если текущие дата и время больше даты и времени начала и 
меньше даты и времени окончания, должны быть выбраны из справочника все клиенты, которые 
указаны в настройках рассылки, и запущена отправка для всех этих клиентов.
•	Если создается рассылка с временем старта в будущем, отправка должна стартовать 
автоматически по наступлению этого времени без дополнительных действий со стороны пользователя 
сервиса.
•	По ходу отправки рассылки должна собираться статистика (см. описание сущностей «Рассылка» 
и «Попытка» выше) по каждой рассылке для последующего формирования отчетов. Попытка создается 
одна для одной рассылки. Формировать попытки рассылки для всех клиентов отдельно не нужно.
•	Внешний сервис, который принимает отправляемые сообщения, может долго обрабатывать запрос, 
отвечать некорректными данными, на какое-то время вообще не принимать запросы. Нужна корректная 
обработка подобных ошибок. Проблемы с внешним сервисом не должны влиять на стабильность работы 
разрабатываемого сервиса рассылок.

Описание задач

•	Расширьте модель пользователя для регистрации по почте, а также верификации.

Используйте для наследования модель AbstractUser.

•	Добавьте интерфейс для входа, регистрации и подтверждения почтового ящика.

Вы уже реализовывали такую задачу в рамках домашних работ. Попробуйте воспроизвести все шаги 
заново, чтобы закрепить процесс работы с кастомными пользователями в Django.

•	Реализуйте ограничение доступа к рассылкам для разных пользователей.
•	Реализуйте интерфейс менеджера.
•	Создайте блог для продвижения сервиса.
Функционал менеджера

•	Может просматривать любые рассылки.
•	Может просматривать список пользователей сервиса.
•	Может блокировать пользователей сервиса.
•	Может отключать рассылки.
•	Не может редактировать рассылки.
•	Не может управлять списком рассылок.
•	Не может изменять рассылки и сообщения.
Функционал пользователя

Весь функционал дублируется из первой части курсовой работы, но теперь нужно следить за тем, 
чтобы пользователь не мог случайным образом изменить чужую рассылку и мог работать только со 
своим списком клиентов и со своим списком рассылок.
Продвижение
Блог

Реализуйте приложение для ведения блога. При этом отдельный интерфейс реализовывать не 
требуется, но необходимо настроить административную панель для контент-менеджера.

В сущность блога добавьте следующие поля:
•	заголовок,
•	содержимое статьи,
•	изображение,
•	количество просмотров,
•	дата публикации.
Главная страница

Реализуйте главную страницу в произвольном формате, но обязательно отобразите следующую 
информацию:

•	количество рассылок всего,
•	количество активных рассылок,
•	количество уникальных клиентов для рассылок,
•	три случайные статьи из блога.
Кеширование

Для блога и главной страницы самостоятельно выберите, какие данные необходимо кешировать, 
а также каким способом необходимо произвести кеширование.


Для запуска проекта необходимо:
- Развернуть виртуальное окружение poetry
- Установить зависимости с помощью `poetry install`
- Создать базу данных `mailshot_site`
- В домашнюю папку **пользователя** добавить
файл `.pg_service.conf`, внутри необходимо указать следующую информацию о базе данных:
    ```ini
    [mailshot_site]
    host=localhost
    user=postgres
    dbname=mailshot_site
    port=5432
    ```
    С помощью `chmod 0600 .pg_service.conf` изменить уровень доступа, иначе файл не будет читаться
- В корневую папку **проекта** добавить файл `.pgpass`\
  Внутри указать информацию следующего вида:
  ```
  localhost:5432:mailshot_site:postgres:<ваш пароль от базы данных>
  ```
  С помощью `chmod 0600 .pgpass` изменить уровень доступа, иначе файл не будет читаться

- Применить миграции с помощью `python manage.py migrate`
- Наполнить базу данных с помощью команды `python manage.py loaddata db.json`

Запустить следующие команды (каждую в своём процессе)
- `redis-server`
- `rabbitmq-server`
- `celery -A conf worker -l info`
- `celery -A conf beat`
- `python manage.py runserver`

для создания суперпользователя можно применить команду `setupsuperuser`