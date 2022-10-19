import json
import time


def main():
    def return_json(path):
        try:
            file_ = open(path, 'r', encoding = "utf8")
            data = json.loads(file_.read())
            file_.close()

            del file_
            
            return {"success": True, "data": data}
        except Exception as err:
            print(err)

        return {"success": False}

    data = return_json('actionless.json')
    data = data.get('data', {})

    ss = sorted(
        data.items(),
        key = lambda x: x[1]['found_time'],
        reverse = True,
    )

    for s in ss:
        print(
            'https://hh.ru/vacancy/%s' % (
                s[0],
            )
        )


if __name__ == '__main__':
    main()