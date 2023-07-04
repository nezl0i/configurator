import sys
from config import config as cfg
from datetime import datetime
from common.logger import LOGGER
from common.colors import c
from functools import wraps


class Repeat:
    def __init__(self, n=None):
        self._n = cfg.REPEAT_COUNT if n is None else n

    def __call__(self, func):
        def inner(*args, **kwargs):
            for _ in range(self._n):
                current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
                check, buffer = func(*args, **kwargs)
                if check:
                    if cfg.DEBUG:
                        print(f'[{current_time}] :{c.FAIL} <<', ' '.join(buffer), c.END)
                        LOGGER.info(f'<< {" ".join(buffer)}')
                    else:
                        sys.stdout.write('Идет обмен данными ...\r')
                    sys.stdout.flush()
                    return check, buffer
                else:
                    if buffer and len(buffer) != 0:
                        if cfg.DEBUG:
                            print(f'[{current_time}] :{c.FAIL} <<', ' '.join(buffer), c.END)
                            LOGGER.info(f'<< {" ".join(buffer)}')
            print(f'{c.WARNING}Нет ответа от устройства.{c.END}')
            LOGGER.info(f'Нет ответа от устройства.')
            sys.exit()
        return inner

    def __repr__(self):
        return f'{self.__class__.__name__}({self._n})'


def repeat(_func=None, *, count=None):
    count = cfg.REPEAT_COUNT if count is None else count

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            for _ in range(count):
                current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
                check, buffer = func(*args, **kwargs)
                if check:
                    if cfg.DEBUG:
                        print(f'[{current_time}] :{c.FAIL} <<', ' '.join(buffer), c.END)
                        LOGGER.info(f'<< {" ".join(buffer)}')
                    else:
                        sys.stdout.write('Идет обмен данными ...\r')
                    sys.stdout.flush()
                    return check, buffer
                else:
                    if buffer and len(buffer) != 0:
                        if cfg.DEBUG:
                            print(f'[{current_time}] :{c.FAIL} <<', ' '.join(buffer), c.END)
                            LOGGER.info(f'<< {" ".join(buffer)}')
            print(f'{c.WARNING}Нет ответа от устройства.{c.END}')
            LOGGER.info(f'Нет ответа от устройства.')
            sys.exit()
        return inner
    if _func is None:
        return wrapper
    else:
        return wrapper(_func)


def multi_repeat(decorators):
    def decor(func):
        def wrapper(*args, **kwargs):
            if kwargs.pop('multi', True):
                return decorators(func)(*args, **kwargs)
            else:
                return decorators(func, count=1)(*args, **kwargs)
        return wrapper
    return decor
