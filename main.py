from hhru import HHRU

import datetime
import random
import json
import time


file_actionless = "actionless.json"
file_settings = "settings.json"


all_orders = [
    {},
    {"order_by": 'publication_time'},
    {"order_by": 'salary_desc'},
    {"order_by": 'salary_asc'},
]


def main():
    def dict_raise_on_duplicates(ordered_pairs):
        """Reject duplicate keys."""
        d = {}

        for k, v in ordered_pairs:
            if k in d:
                raise ValueError(
                    "duplicate key: %r" % (k, )
                )

            else:
                d[k] = v

        return d


    def return_json(path):
        try:
            with open(path, 'r', encoding="utf8") as f:
                data = json.loads(f.read())

            return {"success": True, "data": data}
        except Exception as err:
            print(err)

        return {"success": False}


    def save_json(path, data):
        try:
            with open(path, 'w', encoding="utf8") as f:
                json.dump(data, f)
        except Exception as err:
            print(err)


    def prepare_letter(text, data):
        for tag in [
            'name',
        ]:
            text = text.replace(f'<{tag}>', data.get(tag, ''))
        
        return text


    # user_agents = return_json('agents.json').get('data', {})

    # browsers_dict = user_agents.get('browsers', {})
    # browsers_list = list(browsers_dict.keys())

    # my_agent = random.choice(browsers_dict.get(
    #     browsers_list[random.randint(0, len(browsers_list) - 1)]
    # ))

    # print(my_agent)

    settings = return_json(file_settings)

    if settings.get('success') is False:
        print(
            'Не могу загрузить все настройки из файла %s' % (
                file_settings,
            )
        )

        return
    else:
        settings = settings.get('data')

    actionless = return_json(file_actionless)

    if not actionless.get('success'):
        actionless = {}
    else:
        actionless = actionless.get('data', {})

    hhru_object = HHRU(settings.get('login'), settings.get('password'))

    hhru_object.get_login_session()

    while True:
        bump_time = hhru_object.minimum_time_bump()
        await_time = bump_time - int(time.time())

        if await_time < 0:
            await_time = 0

        print(
            'Ожидаем %i минут перед действиями.\nВремя - %s' % (
                await_time // 60,
                datetime.datetime.fromtimestamp(
                    bump_time).strftime("%d.%m.%y %H:%M:%S"),
            )
        )

        time.sleep(await_time)

        for index_req, resume in enumerate(settings.get('requests', [])):
            # int_order = random.randint(0, len(all_orders) - 1)
            int_order = 0

            prepared_params = resume.get('params', {})

            prepared_params.update(
                all_orders[int_order]
            )

            letter = ''

            try:
                if resume.get('file_letter'):
                    with open(
                        file=resume.get('file_letter'),
                        mode='r',
                        encoding='utf8',
                    ) as f:
                        letter = f.read().strip()

                    print(
                        'Сопроводительное письмо:\n%s' % (
                            str(letter),
                        )
                    )

                else:
                    print(
                        'Сопроводительное письмо - Файл для поиска %i не был найден.\nПерепроверьте файл %s' % (
                            index_req,
                            file_settings,
                        )
                    )

            except FileNotFoundError:
                print(
                    'Сопроводительное письмо - Не найден файл %s.\nСопроводительное письмо заполняется автоматически пустым значением.' % (
                        resume.get('file_letter'),
                    )
                )

            needed_vacancy = []
            response_array = []

            for job in hhru_object.search_vacancy(prepared_params).get('vacancySearchResult', {}).get('vacancies', []):
                # Если никаких дополнительных пометок для нас нет (отказ или отклик)
                if len(job.get('userLabels', [])) == 0:
                    needed_vacancy.append(
                        job
                        # job.get('vacancyId')
                    )

            for vacancy in needed_vacancy:
                prepared_letter = prepare_letter(
                    text = letter,
                    data = vacancy,
                )

                result_ = hhru_object.vacancy_response(
                    vacancyId=vacancy.get('vacancyId'),
                    resume_hash=resume.get('id'),
                    letter=prepared_letter,
                )

                response_array.append(
                    {
                        "id": vacancy.get('vacancyId'),
                        "status": result_,
                    }
                )

                time.sleep(random.uniform(0.1, 1.2))

            for response in response_array:
                print(
                    '%i - https://hh.ru/vacancy/%i ' % (
                        response.get('status'),
                        response.get('id'),
                    )
                )

                if response.get('status') != 200:
                    if not actionless.get(response['id']):
                        actionless[response['id']] = {
                            "found_time": int(time.time()),
                        }

            save_json(
                file_actionless,
                actionless,
            )

        # BUMP RESUME BLOCK

        finded_resume = hhru_object.get_available_resumes_bump()

        time.sleep(random.uniform(1.0, 1.5))

        for resume in finded_resume:
            result = hhru_object.bump_resume(resume['hash'])

            print(
                "%s - https://hh.ru/resume/%s" % (
                    result,
                    resume['hash'],
                )
            )

        print('BUMPED')

        # END BUMP RESUME BLOCK


if __name__ == '__main__':
    main()
