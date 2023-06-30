import requests
import random
import pickle
import time
import json
import os
import re


class HHRU:

    def __init__(self, login: str, password: str, file_session: str = "session.bin", count_requests: int = 10) -> None:
        """
            :param login: str - логин для входа на сайт
            :param password: str - пароль для входа на сайт
            :param * file_session: str - файл для кеширования куки сессии, по дефолту session.bin

            :returns: None
        """

        self.login = login
        self.password = password
        self.file_session = file_session
        self.session = None

        self.count_requests = count_requests

    def xsrftoken(self):
        """
            Функция возвращает xsrf токен в авторизированном аккаунте hh.ru

            :returns: None or str - значение xsrf внутри сессии
        """

        token = None

        for p in self.session.cookies.items():
            if p[0] == '_xsrf':
                token = p[1]

        if not token:
            print('cant handle xsrfToken')

        return token

    def get_resumes(self):
        """
            Функция возвращает найденные резюме на авторизированном аккаунте hh.ru

            :returns: list - значения найденных резюме 
        """

        finded_resume = []

        for _ in range(self.count_requests):
            try:
                res_resumes = self.session.get(
                    url='https://hh.ru/applicant/resumes',
                    params={
                        'hhtmFromLabel': 'header',
                        'disableBrowserCache': 'true',
                    },
                )

                raw_finded_resume = re.findall(
                    pattern=re.compile(
                        '({\"id\": \"([\d]+)\", \"hash\": \"([\d\w]+)\", ([\d\w\,\:\;\'\"\s\-\+\:]+)})'),
                    string=res_resumes.text,
                )

                for rr in raw_finded_resume:
                    parsed = json.loads(rr[0])

                    if parsed.get('status') in ['not_finished']:
                        continue

                    finded_resume.append(
                        parsed
                    )

                break
            except Exception as e:
                print(e)

        return finded_resume

    def get_available_resumes_bump(self):
        """
            Функция возвращает доступные резюме для бампа на авторизированном аккаунте hh.ru

            :returns: list - значения найденных резюме для бампа
        """

        resumes = self.get_resumes()
        result = []

        for resume in resumes:
            update_time_resume = int(
                (resume.get('updated') + resume.get('update_timeout', 14400000)) / 1000)

            if update_time_resume < int(time.time()):
                result.append(resume)

        return result

    def minimum_time_bump(self):
        """
            Функция возвращает значения ближайшего подъема резюме на авторизированном аккаунте hh.ru

            :returns: int - значение ближайшего бампа
        """

        resumes = self.get_resumes()

        near_bump_time = int(
            (resumes[0].get('updated') + resumes[0].get('update_timeout', 14400000)) / 1000)

        for resume in resumes:
            update_time_resume = int(
                (resume.get('updated') + resume.get('update_timeout', 14400000)) / 1000)

            if update_time_resume < near_bump_time:
                near_bump_time = update_time_resume

        return near_bump_time

    def search_vacancy(self, params):
        """
            Функция поиска открытых вакансий на сайте hh.ru

            :param params: dict - запрос с поиском работы на сайт

            :returns: dict - результат выполнения запроса
        """

        for _ in range(self.count_requests):
            try:
                search_result = self.session.get(
                    url='https://hh.ru/shards/vacancy/search',
                    params=params,
                )

                return search_result.json()
            except Exception as e:
                print(e)

        return {}

    def just_login(self):
        """
            Функция выполняет авторизацию на сайте hh.ru

            :returns: requsts.session - возвращает сессию на сайте hh.ru
        """

        self.session = requests.session()

        for _ in range(self.count_requests):
            try:
                temp_res = self.session.get(
                    url='https://hh.ru/account/login',
                    params={
                        'backurl': '/',
                        'hhtmFrom': 'main',
                    },
                    headers={
                        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
                        'referer': 'https://hh.ru/',
                        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'document',
                        'sec-fetch-mode': 'navigate',
                        'sec-fetch-site': 'same-origin',
                        'sec-fetch-user': '?1',
                        'upgrade-insecure-requests': '1',
                    }
                )

                res_login = self.session.post(
                    url='https://hh.ru/account/login',
                    params={
                        'backurl': '/',
                        'hhtmFrom': 'main',
                    },
                    headers={
                        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
                        'referer': 'https://hh.ru/',
                        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'document',
                        'sec-fetch-mode': 'navigate',
                        'sec-fetch-site': 'same-origin',
                        'sec-fetch-user': '?1',
                        'upgrade-insecure-requests': '1',
                        'x-xsrftoken': self.xsrftoken(),
                    },
                    data={
                        '_xsrf': self.xsrftoken(),
                        'backUrl': 'https://hh.ru/',
                        'failUrl': '/account/login?backurl=%2F',
                        'remember': 'yes',
                        'username': self.login,
                        'password': self.password,
                        'isBot': 'false'
                    }
                )

                if res_login.status_code != 200:
                    print('cant login')

                self.session.headers.update(
                    {
                        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
                        'referer': 'https://hh.ru/',
                        'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'document',
                        'sec-fetch-mode': 'navigate',
                        'sec-fetch-site': 'same-origin',
                        'sec-fetch-user': '?1',
                        'upgrade-insecure-requests': '1',
                        'x-xsrftoken': self.xsrftoken(),
                    }
                )

                break
            except Exception as e:
                print(e)

        return self.session

    def ping_request(self):
        """
            Функция для проверки доступности сайта hh.ru (используется для проверки авторизации, если пользователь авторизирован, возвращает True)

            :returns: bool - результат выполнения пинг запроса на сайт hh.ru
        """

        if self.session:
            for _ in range(self.count_requests):
                try:
                    ping_login_request = self.session.get('https://hh.ru/')

                    if ping_login_request.status_code != 200:
                        self.session = self.just_login()
                    elif ping_login_request.status_code == 200:
                        return True

                except Exception as e:
                    print(e)

                rnd = random.randint(1, 10)
                print(
                    'ПИНГ: Запрос прошел неудачно, попробую еще раз через %i секунд' % (rnd))

                time.sleep(rnd)

        else:
            print('ПИНГ: Сессия пустая, запрос неудачный!')

        print('ПИНГ: Результат выполнения функции неудачный!')

        return False

    def save_session_from_file(self):
        """
            Функция сериализации сессии в файл

            :returns: None
        """

        with open(self.file_session, 'wb') as f:
            pickle.dump(self.session.cookies, f)

    def return_session_from_file(self):
        """
            Функция для десериализации сессии из файла

            :returns: requests.session or None - результат десериализации сессии
        """

        if os.path.exists(self.file_session) is False:
            return None

        self.session = requests.session()

        with open(self.file_session, 'rb') as f:
            self.session.cookies.update(pickle.load(f))

        self.session.headers.update(
            {
                'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
                'referer': 'https://hh.ru/',
                'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
                'sec-fetch-dest': 'document',
                'sec-fetch-mode': 'navigate',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-user': '?1',
                'upgrade-insecure-requests': '1',
                'x-xsrftoken': self.xsrftoken(),
            }
        )

        return self.session

    def get_login_session(self):
        """
            Главная функция аунтификации, десериализует сессию, пытается сделать пинг запрос, если все окей, возвращает сессию, если все плохо, пытается авторизоваться по новой.

            :returns: None
        """

        if self.return_session_from_file() is not None:
            if self.ping_request() is True:
                self.save_session_from_file()

                return self.session

        self.session = self.just_login()

        if self.ping_request():
            self.save_session_from_file()

        return self.session

    def bump_resume(self, resume_hash: str):
        """
            Функция поднятия резюме в поиске на авторизированном сайте hh.ru

            :param resume_hash: str - hash-id резюме для поднятия

            :returns: int - статус код выполнения поднятия резюме
        """

        for _ in range(self.count_requests):
            try:
                return self.session.post(
                    url='https://hh.ru/applicant/resumes/touch',
                    data={
                        'resume': resume_hash,
                        'undirectable': 'true',
                    },
                ).status_code
            except Exception as e:
                print(e)

        return 0

    def vacancy_response(self, vacancyId: int, resume_hash: str, letter: str = ""):
        """
            Функция отклика на вакансию на авторизированном сайте hh.ru

            :param vacancyId: int - id вакансии для отклика
            :param resume_hash: str - hash-id резюме для отклика
            :param letter: str - сопроводительное письмо, по дефолту заполняется пустым значением

            :returns: int - статус код выполнения поднятия резюме
        """

        for _ in range(self.count_requests):
            try:
                return self.session.post(
                    url='https://hh.ru/applicant/vacancy_response/popup',
                    data={
                        '_xsrf': self.xsrftoken(),
                        'vacancy_id': vacancyId,
                        'resume_hash': resume_hash,
                        'ignore_postponed': 'true',
                        'incomplete': 'false',
                        'letter': letter,
                        'lux': 'true',
                        'withoutTest': 'no',
                        'hhtmFromLabel': 'undefined',
                        'hhtmSourceLabel': 'undefined',
                    },
                ).status_code
            except Exception as e:
                print(e)

        return 0


if __name__ == '__main__':
    hhruobject = HHRU()
