import re
import time
import json
import requests


def main():
    def xsrftoken(session):
        token = None

        if False:
            ttoken = re.search(
                re.compile('"xsrfToken": "([\w\d]+)", '),
                res.text,
            )

            if ttoken:
                token = ttoken.group(1)
        
        else:
            for p in session.cookies.items():
                if p[0] == '_xsrf':
                    token = p[1]
            
        if not token:
            print('cant handle xsrfToken')

        return token    


    def get_resumes(session):
        finded_resume = []

        res_resumes = session.get(
            url = 'https://hh.ru/applicant/resumes',
            # params = {
            #     'hhtmFromLabel': 'header',
            #     'disableBrowserCache': 'true',
            # },
            headers = {
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
                'x-xsrftoken': xsrftoken(session = session),
            },
        )

        raw_finded_resume = re.findall(
            pattern = re.compile('({"id": "([\d]+)", "hash": "([\d\w]+)", ([\d\w\,\:\;\'\"\s\-\+\:]+)})'),
            # pattern = re.compile('"applicableResumes": \[(\"[\d\w]+\"[, ]*)+\]'),
            string = res_resumes.text,
        )

        for rr in raw_finded_resume:
            parsed = json.loads(rr[0])

            if parsed.get('status') in ['not_finished']:
                continue

            finded_resume.append(
                parsed
            )

        return finded_resume

    
    def get_available_resumes_bump(session):
        resumes = get_resumes(session = session)
        result = []

        for resume in resumes:
            update_time_resume = int((resume.get('updated') + resume.get('update_timeout', 14400000)) / 1000)

            if update_time_resume < int(time.time()):
                result.append(resume)
 
        return result

    
    def minimum_time_bump(session):
        resumes = get_resumes(session = session)

        near_bump_time = int((resumes[0].get('updated') + resumes[0].get('update_timeout', 14400000)) / 1000)

        for resume in resumes:
            update_time_resume = int((resume.get('updated') + resume.get('update_timeout', 14400000)) / 1000)

            if update_time_resume < near_bump_time:
                near_bump_time = update_time_resume

        return near_bump_time
    

    def search_vacancy(session, params):
        search_result = session.get(
            url = 'https://hh.ru/shards/vacancy/search',
            params = params,
            headers = {
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
                'x-xsrftoken': xsrftoken(session = session),
            }
        )

        try:
            return search_result.json()
        except Exception as e:
            print(e)

        return {}


    def get_login_session(login, password):
        session = requests.session()

        session.get(
            url = 'https://hh.ru/account/login',
            params = {
                'backurl': '/',
                'hhtmFrom': 'main',
            },
            headers = {
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

        res_login = session.post(
            url = 'https://hh.ru/account/login',
            params = {
                'backurl': '/',
                'hhtmFrom': 'main',
            },
            headers = {
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
                'x-xsrftoken': xsrftoken(session = session),
            },
            data = {
                '_xsrf': xsrftoken(session = session),
                'backUrl': 'https://hh.ru/',
                'failUrl': '/account/login?backurl=%2F',
                'remember': 'yes',
                'username': login,
                'password': password,
                'username': login,
                'isBot': 'false'
            }
        )

        if res_login.status_code != 200:
            print('cant login')

        return session


    settings = open(file = 'settings.txt', mode = 'r', encoding = 'utf8').readlines()

    login = settings[0].strip()
    password = settings[1].strip()

    session = get_login_session(login = login, password = password)

    while True:
        await_time = minimum_time_bump(session = session) - int(time.time())

        if await_time < 0:
            await_time = 0

        time.sleep(await_time)

        search_data = search_vacancy(
            session = session, 
            params = {
                'area': '1', # Регион: 1 - Москва
                'schedule': 'fullDay', # remote - удаленка, fullDay - полный рабочий день, flexible - гибкий график
                'search_field': 'name', # Ключевые слова В названии вакансии
                'search_field': 'company_name', # Ключевые слова В названии компании 
                'search_field': 'description', # Ключевые слова В описании вакансии
                'salary': '120000', # Зарплата - 120к
                'only_with_salary': 'true', # Только с зарплатой
                'text': 'python', # Текст поиска
                'from': 'suggest_post',
                'clusters': 'true',
                'ored_clusters': 'true',
                'order_by': 'publication_time', # Сортируем по новизне
                'enable_snippets': 'true',
            }
        )

        my_resume_hash = 'ac940fc5ff0b2962b60039ed1f634651786347'

        for job in search_data.get('vacancySearchResult', {}).get('vacancies', []):
            if not job.get('@responseLetterRequired'): # смотрим что бы без письма была эта штука
                if len(job.get('userLabels', [])) == 0: # Если никаких дополнительных пометок для нас нет (отказ или отклик)
                    result_ = session.post(
                        url = 'https://hh.ru/applicant/vacancy_response/popup',
                        data = {
                            '_xsrf': xsrftoken(session = session),
                            'vacancy_id': job.get('vacancyId'),
                            'resume_hash': my_resume_hash,
                            'ignore_postponed': 'true',
                            'incomplete': 'false',
                            'letter': '',
                            'lux': 'true',
                            'withoutTest': 'no',
                            'hhtmFromLabel': 'undefined',
                            'hhtmSourceLabel': 'undefined',
                        },
                        headers = {
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
                            'x-xsrftoken': xsrftoken(session = session),
                        }
                    )

                    print('%i - https://hh.ru/vacancy/%i ' % (result_.status_code, job.get('vacancyId'), ))
        
        finded_resume = get_available_resumes_bump(session = session)

        # original_request_id = re.search(
        #     pattern = re.compile('requestId: "([\d\w]+)",'),
        #     string = res_resumes.text,
        # )

        for resume in finded_resume:
            result = session.post(
                url = 'https://hh.ru/applicant/resumes/touch',
                data = {
                    'resume': resume['hash'],
                    'undirectable': 'true',
                },
                headers = {
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
                    'x-xsrftoken': xsrftoken(session = session),
                },
            )

            print(result.status_code)

        print('BUMPED')


if __name__ == '__main__':
    main()