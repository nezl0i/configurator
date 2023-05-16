from common.colors import c


def check_out(tmp):
    return {
        tmp == "00": "OK",
        tmp == "01": "Недопустимая команда или параметр",
        tmp == "02": "Внутренняя ошибка счетчика",
        tmp == "03": "Недостаточен уровень для удовлетворения запроса",
        tmp == "04": "Внутренние часы счетчика уже корректировались в течение текущих суток",
        tmp == "05": "Не открыт канал связи"
    }[True]


def check_response(text, out):
    try:
        print(f'{c.GREEN}{text} - {check_out(out[1])}{c.END}\n')
    except KeyError:
        print(f'{c.GREEN}{text} - Ошибка{c.END}\n')
