<h1 align="center">
  hhru - проще, чем когда-либо!
</h1>


<h4 align="center">Оглавление README:</h4>
<div align="center">
    <a href="#про-скрипт"> • Для чего нужен этот скрипт • </a><br>
    <a href="#установка"> • Установка • </a><br>
    <a href="#внутрянка"> • Что внутри • </a><br>
    <a href="#файл-settingsjson"> • Что такое файл settings.json • </a><br>
    <a href="#примечание"> • Примечание • </a>
</div>

<div>
    <h2 dir="auto">
        <a id="user-content-про-скрипт" class="anchor" aria-hidden="true" href="#про-скрипт">
            <svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true">
                <path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z">
                </path>
            </svg>
        </a>
        Про скрипт
    </h2>
    
    <p dir="auto">Данный скрипт предназначен для сайта hh.ru.</p>
    <p dir="auto">
        Изначально был задуман как альтернативное решение для автобампа резюме, потом, глянув просмотры эффективность работы этой идеи было принято решение добавить поддержку отклика на вакансии с резюме. По итогу, как предполагалось, компании стали активнее просматривать мое резюме и чаще давать приглашение на открытые вакансии.
    </p>
    
    <a target="_blank" rel="noopener noreferrer" href="/Dangeres/hhru/blob/master/hhru.png"><img src="/Dangeres/hhru/blob/master/hhru.png" alt="Красивая картиночка :)" style="max-width: 100%;"></a>
</div>

<div>
    <h2 dir="auto">
        <a id="user-content-про-скрипт" class="anchor" aria-hidden="true" href="#установка">
            <svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true">
                <path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z">
                </path>
            </svg>
        </a>
        Установка
    </h2>
    
    <ol dir="auto">
        <li>Скачиваете ветку;</li>
        <li>Устанавливаете python 3.9;</li>
        <li>Редактируете файл <code>settings.json</code> под себя;</li>
        <li>Запускаете <code>autobump.py</code> и наслаждаетесь результатом.</li>
    </ol>
</div>


<div>
    <h2 dir="auto">
        <a id="user-content-про-скрипт" class="anchor" aria-hidden="true" href="#внутрянка">
            <svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true">
                <path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z">
                </path>
            </svg>
        </a>
        Внутрянка
    </h2>
    
    <ol dir="auto">
        <li>Данные для настройки указываются в конфиг файле <code>settings.json</code> <em>(шаблон заполнен тестовыми данными и называется sample_settings.json)</em>;</li>
        <li>Автоматизированная программа(скрипт) авторизируется на hh.ru по вашим данным из файла конфига;</li>
        <li>Скрипт получает все резюме для бампа и выжидает время для поднятия;</li>
        <li>Скрипт получает все вакансии по вашему запросу и дает отклик с вашим резюме;</li>
        <li>Затем скрипт автоматически поднимает все ваши резюме и переходит на пункт 3.</li>
    </ol>
</div>

<div>
    <h2 dir="auto">
        <a id="user-content-про-скрипт" class="anchor" aria-hidden="true" href="#файл-settingsjson">
            <svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true">
                <path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z">
                </path>
            </svg>
        </a>
        Файл settings.json
    </h2>
    
    <ul dir="auto">
        <li>
            <p dir="auto">"login": строка с содержимым в виде почты от сайта hhru</p>
        </li>
        
        <li>
            <p dir="auto">"password": строка с содержимым в виде пароля от сайта hhru</p>
        </li>
        
        <li>
            <p dir="auto">"requests": массив с содержимым словариками для поиска вакансий</p>
            <ul dir="auto">
                <li>Каждый словарь имеет следующие поля:
                    <ul dir="auto">
                        <li>
                            <p dir="auto">"id": строка с содержимым в виде айди резюме для отклика на поиск от сайта hhru.
                            Найти данную строку можно пройдя по ссылке <a href="https://hh.ru/applicant/resumes" rel="nofollow">https://hh.ru/applicant/resumes</a>
                            Находим нужное резюме, переходим по нему.</p>
                            
                            <p dir="auto"><a target="_blank" rel="noopener noreferrer" href="/Dangeres/hhru/blob/master/resume.png"><img src="/Dangeres/hhru/raw/master/resume.png" alt="Находим нужное резюме" style="max-width: 100%;"></a></p>
                            <p dir="auto">Смотрим в адресной строке ссылку, копируем данные после hh.ru/resume</p>
                            <p dir="auto"><a target="_blank" rel="noopener noreferrer" href="/Dangeres/hhru/blob/master/resume2.png"><img src="/Dangeres/hhru/raw/master/resume2.png" alt="Айди резюме" style="max-width: 100%;"></a></p>
                        </li>
        
                        <li>
                            <p dir="auto">"params": словарь с полями для поиска</p>
                        </li>
                         
                        <li>
                            <p dir="auto">"file_letter": строка с содержимым названия файла для отклика на найденную по запросу вакансию с отправкой сопроводительного письма.</p>
                        </li>
                    </ul>
                </li>
        </ul>
        </li>
    </ul>
</div>


<div>
    <h2 dir="auto">
        <a id="user-content-про-скрипт" class="anchor" aria-hidden="true" href="#примечание">
            <svg class="octicon octicon-link" viewBox="0 0 16 16" version="1.1" width="16" height="16" aria-hidden="true">
                <path fill-rule="evenodd" d="M7.775 3.275a.75.75 0 001.06 1.06l1.25-1.25a2 2 0 112.83 2.83l-2.5 2.5a2 2 0 01-2.83 0 .75.75 0 00-1.06 1.06 3.5 3.5 0 004.95 0l2.5-2.5a3.5 3.5 0 00-4.95-4.95l-1.25 1.25zm-4.69 9.64a2 2 0 010-2.83l2.5-2.5a2 2 0 012.83 0 .75.75 0 001.06-1.06 3.5 3.5 0 00-4.95 0l-2.5 2.5a3.5 3.5 0 004.95 4.95l1.25-1.25a.75.75 0 00-1.06-1.06l-1.25 1.25a2 2 0 01-2.83 0z">
                </path>
            </svg>
        </a>
        Примечание
    </h2>
    
    <p dir="auto">Скрипт работает с встроенными библиотеками, никакие дополнительные библиотеки ему не нужны.
Работа из коробки - мой взгляд на многие вещи.</p>
</div>