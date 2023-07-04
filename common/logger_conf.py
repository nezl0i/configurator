import logging.handlers
import logging
import os

ENCODING = 'utf-8'

# Уровень логирования
LOGGING_LEVEL = logging.DEBUG

APP_FORMATTER = logging.Formatter('[%(levelname)s] - %(asctime)s  [%(module)s] %(message)s')
# PATH = os.path.dirname('log')
PATH = os.path.join('log', 'logging.log')

# Потоки
STEAM_HANDLER = logging.StreamHandler()
STEAM_HANDLER.setFormatter(APP_FORMATTER)
STEAM_HANDLER.setLevel(logging.DEBUG)

# FILE_HANDLER = logging.handlers.TimedRotatingFileHandler(PATH, encoding=ENCODING, when='M', interval=60)
FILE_HANDLER = logging.handlers.RotatingFileHandler(PATH, maxBytes=1000000, backupCount=10)
FILE_HANDLER.suffix = '%d-%m-%Y'
FILE_HANDLER.setFormatter(APP_FORMATTER)

# Регистратор
LOGGER = logging.getLogger('app')
# LOGGER.addHandler(STEAM_HANDLER)
LOGGER.addHandler(FILE_HANDLER)
LOGGER.setLevel(LOGGING_LEVEL)

if __name__ == '__main__':
    LOGGER.critical('Критическая ошибка')
    LOGGER.error('Ошибка')
    LOGGER.warning('Предупреждение')
    LOGGER.debug('Отладочная информация')
    LOGGER.info('Информационное сообщение')
