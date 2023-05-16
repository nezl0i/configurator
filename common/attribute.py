import sys
from config import config as cfg


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class IAttribute(metaclass=Singleton):
    def __init__(self):
        self.DEVICE_ID = format(cfg.DEVICE_ID, '02X')
        self.DEVICE_LEVEL = format(cfg.DEVICE_LEVEL, '02X')
        self.CONNECT_MODE = cfg.CONNECT_MODE
        self.FIRMWARE_FILE = cfg.FIRMWARE_FILE
        self.CSD_PHONE = cfg.CSD_PHONE
        self.TCP_HOST = cfg.TCP_HOST
        self.TCP_PORT = cfg.TCP_PORT
        self.TCP_TIMEOUT = cfg.TCP_TIMEOUT
        self.DEVICE_PASSWORD = self.set_password(cfg.DEVICE_PASSWORD)
        self.DEVICE_SERIAL_NUMBER = None
        self.DEVICE_WORK_DATA = None
        self.DEVICE_VERSION = None
        self.DEVICE_REVISION = None
        self.DEVICE_CRC = None
        self.DEVICE_IMPULSE = None
        self.FIRMWARE_FILE = cfg.FIRMWARE_FILE
        self.CLEAR_EVENTS_FILE = cfg.CLEAR_EVENTS_FILE
        self.METERS_FILE = cfg.METERS_FILE

    @staticmethod
    def set_password(passwd):
        match cfg.DEVICE_PASSWORD_MODE:
            case 'hex':
                password = ' '.join((format(int(i), '02X')) for i in passwd)
            case 'ascii':
                password = ' '.join((format(ord(i), '02X')) for i in passwd)
            case _:
                print('No pass_mode.')
                sys.exit()
        return password
