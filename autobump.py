import re
import time
import json
import requests


def main():
    settings = open(file = 'settings.txt', mode = 'r', encoding = 'utf8').readlines()

    login = settings[0].strip()
    password = settings[1].strip()

    session = requests.session()

    res = session.get(
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

        return

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
            'x-xsrftoken': token,
        },
        data = {
            '_xsrf': token,
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

    near_bump_time = 0

    while True:
        await_time = 0

        if near_bump_time > 0:
            await_time = int(time.time()) - near_bump_time

        time.sleep(await_time)

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
                'x-xsrftoken': token,
            },
        )

        finded_resume = []

        raw_finded_resume = re.findall(
            pattern = re.compile('({"id": "([\d]+)", "hash": "([\d\w]+)", ([\d\w\,\:\;\'\"\s\-\+\:]+)})'),
            # pattern = re.compile('"applicableResumes": \[(\"[\d\w]+\"[, ]*)+\]'),
            string = res_resumes.text,
        )

        for rr in raw_finded_resume:
            parsed = json.loads(rr[0])

            update_time_resume = int((parsed.get('updated') + parsed.get('update_timeout', 14400000)) / 1000)

            if update_time_resume < near_bump_time or near_bump_time == 0:
                near_bump_time = update_time_resume

            if parsed.get('status') not in ['not_finished'] and update_time_resume <= int(time.time()):
                print(parsed)

                finded_resume.append(
                    parsed
                )

        # raw_finded_resume = re.search( # shit solution, i dont like that #TODO
        #     pattern = re.compile('"applicableResumes": \[((\"[\d\w]+\"[, ]*)+)\]'),
        #     string = res_resumes.text,
        # )
        
        # if raw_finded_resume:
        #     finded_resume = re.findall(
        #         re.compile('"([\d\w]+)\"'),
        #         raw_finded_resume.group(1),
        #     )

        original_request_id = re.search(
            pattern = re.compile('requestId: "([\d\w]+)",'),
            string = res_resumes.text,
        )

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
                    'x-xsrftoken': token,
                },
            )
            
            # result = session.post(
            #     url = 'https://hh.ru/analytics',
            #     params = {
            #         'hhtmSource': 'resume_list',
            #         'hhtmFrom': '',
            #         'hhtmSourceLabel': '',
            #         'hhtmFromLabel': '',
            #         'event': 'button_click',
            #         'buttonName': 'resume_update',
            #         'resumeId': resume['id'],
            #         'originalRequestId': original_request_id,
            #     },
            #     headers = {
            #         'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
            #         'referer': 'https://hh.ru/',
            #         'sec-ch-ua': '"Google Chrome";v="105", "Not)A;Brand";v="8", "Chromium";v="105"',
            #         'sec-ch-ua-mobile': '?0',
            #         'sec-ch-ua-platform': '"Windows"',
            #         'sec-fetch-dest': 'document',
            #         'sec-fetch-mode': 'navigate',
            #         'sec-fetch-site': 'same-origin',
            #         'sec-fetch-user': '?1',
            #         'upgrade-insecure-requests': '1',
            #         # 'x-xsrftoken': token,
            #     },
            # )

            print(result.status_code)

        print('BUMPED')


if __name__ == '__main__':
    main()