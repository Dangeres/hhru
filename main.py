from hhru import HHRU

import datetime
import random
import json
import time
import os

file_actionless = "actionless.json"
file_settings = "settings.json"

all_orders = [
    {},
    {"order_by": 'publication_time'},
    {"order_by": 'salary_desc'},
    {"order_by": 'salary_asc'},
]

def dict_raise_on_duplicates(ordered_pairs):
    """Reject duplicate keys."""
    d = {}
    for k, v in ordered_pairs:
        if k in d:
            raise ValueError("duplicate key: %r" % (k,))
        else:
            d[k] = v
    return d

def return_json(path):
    try:
        with open(path, 'r', encoding="utf8") as f:
            data = json.load(f)
        return {"success": True, "data": data}
    except json.JSONDecodeError as err:
        print(f"Ошибка при разборе JSON в файле {path}: {err}")
    except Exception as err:
        print(f"Ошибка при чтении файла {path}: {err}")
    return {"success": False}

def save_json(path, data):
    try:
        with open(path, 'w', encoding="utf8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as err:
        print(f"Ошибка при сохранении файла {path}: {err}")

def prepare_letter(text, data):
    for tag in ['name']:
        text = text.replace(f'<{tag}>', data.get(tag, ''))
    return text

def main():
    settings = return_json(file_settings)
    if settings.get('success') is False:
        print(f'Не могу загрузить все настройки из файла {file_settings}')
        return
    else:
        settings = settings.get('data')

    actionless = return_json(file_actionless)
    if not actionless.get('success'):
        actionless = {"vacancies": {}}
    else:
        actionless = actionless.get('data', {"vacancies": {}})

    hhru_object = HHRU(settings.get('login'), settings.get('password'))
    hhru_object.get_login_session()

    while True:
        bump_time = hhru_object.minimum_time_bump()
        if bump_time is None:
            print("Невозможно определить время для поднятия резюме. Ожидание 1 час.")
            time.sleep(3600)  # Ожидание 1 час
            continue

        await_time = bump_time - int(time.time())

        if await_time < 0:
            await_time = 0

        print(
            'Ожидаем %i минут перед действиями.\nВремя - %s' % (
                await_time // 60,
                datetime.datetime.fromtimestamp(bump_time).strftime("%d.%m.%y %H:%M:%S"),
            )
        )

        time.sleep(await_time)

        for index_req, resume in enumerate(settings.get('requests', [])):
            int_order = 0
            prepared_params = resume.get('params', {})
            prepared_params.update(all_orders[int_order])

            letter = ''
            try:
                if resume.get('file_letter'):
                    with open(resume.get('file_letter'), 'r', encoding='utf8') as f:
                        letter = f.read().strip()
                    print(f'Сопроводительное письмо:\n{letter}')
                else:
                    print(f'Сопроводительное письмо - Файл для поиска {index_req} не был найден.\nПерепроверьте файл {file_settings}')
            except FileNotFoundError:
                print(f'Сопроводительное письмо - Не найден файл {resume.get("file_letter")}.\nСопроводительное письмо заполняется автоматически пустым значением.')

            needed_vacancy = []
            response_array = []

            for job in hhru_object.search_vacancy(prepared_params).get('vacancySearchResult', {}).get('vacancies', []):
                if len(job.get('userLabels', [])) == 0:
                    needed_vacancy.append(job)

            for vacancy in needed_vacancy:
                prepared_letter = prepare_letter(text=letter, data=vacancy)
                result_ = hhru_object.vacancy_response(
                    vacancyId=vacancy.get('vacancyId'),
                    resume_hash=resume.get('id'),
                    letter=prepared_letter,
                )
                response_array.append({"id": vacancy.get('vacancyId'), "status": result_})
                time.sleep(random.uniform(0.1, 1.2))

            for response in response_array:
                print(f'{response.get("status")} - https://hh.ru/vacancy/{response.get("id")}')
                if response.get('status') != 200:
                    if not actionless["vacancies"].get(str(response['id'])):
                        actionless["vacancies"][str(response['id'])] = {"found_time": int(time.time())}

            save_json(file_actionless, actionless)

        # BUMP RESUME BLOCK
        finded_resume = hhru_object.get_available_resumes_bump()
        time.sleep(random.uniform(1.0, 1.5))

        for resume in finded_resume:
            result = hhru_object.bump_resume(resume['hash'])
            print(f"{result} - https://hh.ru/resume/{resume['hash']}")

        print('BUMPED')
        # END BUMP RESUME BLOCK

if __name__ == '__main__':
    main()
