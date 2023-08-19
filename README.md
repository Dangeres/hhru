<h1 align="center">
  hhru - проще, чем когда-либо!
</h1>


<h4 align="center">Оглавление README:</h4>
<div align="center">
    <a href="#про-скрипт"> • Для чего нужен этот скрипт • </a><br>
    <a href="#установка"> • Установка • </a><br>
    <a href="#внутрянка"> • Что внутри • </a><br>
    <a href="#файл-settingsjson"> • Что такое файл settings.json • </a><br>
    <a href="#шаблон-для-сопроводительного-письма"> • Шаблон сопроводительных писем • </a><br>
    <a href="#примечание"> • Примечание • </a>
</div>


## Про скрипт
Данный скрипт предназначен для сайта hh.ru.

Изначально был задуман как альтернативное решение для автобампа резюме, потом, глянув просмотры и эффективность работы этой идеи было принято решение добавить поддержку отклика на вакансии с резюме. По итогу, как и предполагалось, компании стали активнее просматривать мое резюме и чаще давать приглашение на открытые вакансии.


![Красивая картиночка :)](/images/hhru.png)

![Вторая красивая картиночка :)](/images/hhru2.png)


## Установка
1. Скачиваете ветку;
2. Устанавливаете python 3.9;
3. Создаете виртуальное окружение `python3.9 -m venv env`
4. Активируете виртуальное окружение и устанавливаете зависимости `pip install -r requirements.txt`
5. Редактируете файл `settings.json` под себя;
6. Запускаете `main.py` и наслаждаетесь результатом.


## Внутрянка
1. Данные для настройки указываются в конфиг файле `settings.json` *(шаблон заполнен тестовыми данными и называется sample_settings.json)*;
2. Автоматизированная программа(скрипт) авторизируется на hh.ru по вашим данным из файла конфига;
3. Скрипт получает все резюме для бампа и выжидает время для поднятия;
4. Скрипт получает все вакансии по вашему запросу и дает отклик с вашим резюме;
5. Затем скрипт автоматически поднимает все ваши резюме и переходит на пункт 3.


## Файл settings.json
Файл settings.json имеет формат json, с следующими ключами:

* "login": строка с содержимым в виде почты от сайта hhru,

* "password": строка с содержимым в виде пароля от сайта hhru,

* "requests": массив с содержимым словариками для поиска вакансий
  * Каждый словарь имеет следующие поля:
    - "id": строка с содержимым в виде айди резюме для отклика на поиск от сайта hhru.
      Найти данную строку можно пройдя по ссылке https://hh.ru/applicant/resumes
      Находим нужное резюме, переходим по нему.

      ![Находим нужное резюме](/images/resume.png)

      Смотрим в адресной строке ссылку, копируем данные после hh.ru/resume

      ![Айди резюме](/images/resume2.png)

    - "params": словарь с полями для поиска

    - "file_letter": строка с содержимым названия файла для отклика на найденную по запросу вакансию с отправкой сопроводительного письма.


## Шаблон для сопроводительного письма
В шаблон сопроводительного письма можно добавить уникальность в виде переменных которые прилагаются к письму, список доступных переменных:

`name` - *Наименование вакансии (титульник)*


## Примечание
По работе с виртуальными окружениями можно почитать <a href="https://docs.python.org/3/library/venv.html#how-venvs-work"> docs.python.org</a>