import functools
import sys


def is_status(method):
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.status:
            return method(self, *args, **kwargs)
        print('Не авторизован!')
        sys.exit()
    return wrapper
