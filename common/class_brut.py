import os
import sys
import socket
from time import sleep
from sys import platform
from config import config as cfg
from common.modbus_crc16 import crc16
from common.uart import UartSerialPort

try:
    from progress.bar import IncrementalBar
except ImportError:
    if platform.startswith('win'):
        os.system('py -m pip install progress')
    else:
        os.system('python3 -m pip install progress')
    from progress.bar import IncrementalBar


class Brutforce(UartSerialPort):
    def __init__(self):
        super().__init__()

        self.id = format(cfg.DEVICE_ID, '02X')

        self.start_passwd = cfg.START_PASSWORD
        self.stop_passwd = cfg.STOP_PASSWORD
        self.pass_mode = cfg.DEVICE_PASSWORD_MODE

        self.mode = cfg.CONNECT_MODE

        self.s = None
        self.TCP_HOST = cfg.TCP_HOST
        self.TCP_PORT = cfg.TCP_PORT
        self.TCP_TIMEOUT = cfg.TCP_TIMEOUT
        self.flag = False

        self.bar = IncrementalBar('Выполнение', max=self.stop_passwd - self.start_passwd)
        self._check_test()

    def __test(self, pk):
        test = f'{pk} 00 '
        transfer = bytearray.fromhex(test + crc16(bytearray.fromhex(test)))
        sys.stdout.write(f'Тест канала связи ...\r')
        if self.mode == 2:
            self.s.send(transfer)
            buffer = self.s.recv(4)
        else:
            self.set_timeout(self.timeout)
            self.sp.write(transfer)
            buffer = self.sp.read(4)
        while buffer:
            sys.stdout.write(f'Тест канала связи - ОК.\n')
            print('-' * 28)
            sleep(1)
            return True
        return False

    def _check_test(self):
        if self.__test(self.id):
            self.flag = True
        else:
            print('Нет ответа от устройства')
            sys.exit()

    def socket_connect(self):
        self.flag = False
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('Socket successfully created')
            self.s.connect((self.TCP_HOST, self.TCP_PORT))
            self.s.settimeout(self.TCP_TIMEOUT)
            print(f'Connected to {self.TCP_HOST}:{self.TCP_PORT}\n')
            self._check_test()
        except socket.error as err:
            print(err)
            sys.exit()

    def reading(self, pk, input_pass=None):
        test = f'{pk} 01 02 {input_pass} '
        transfer = bytearray.fromhex(test + crc16(bytearray.fromhex(test)))
        sys.stdout.write(f' [Пробуем пароль - {input_pass}]\r')
        self.bar.next()
        if self.mode == 2:
            self.s.send(transfer)
            buffer = self.s.recv(4)
        else:
            # self.set_timeout(1)
            self.sp.write(transfer)
            buffer = self.sp.read(4)

        while buffer:
            print(f"Ответ от устройства >> {buffer.hex(' ', -1)}\n")
            print(f'Пароль найден - {input_pass}')
            with open('log/password/password.txt', 'w') as f:
                f.write(input_pass)
            self.bar.finish()
            return True
        return False

    def brut_password(self):
        if self.flag:
            while self.start_passwd <= self.stop_passwd:
                if self.pass_mode == 'hex':
                    hex_password = ' '.join((format(int(i), '02X')) for i in str(self.start_passwd).zfill(6))
                elif self.pass_mode == 'ascii':
                    hex_password = ' '.join((format(ord(i), '02X')) for i in str(self.start_passwd).zfill(6))
                else:
                    print('Pass_mode is None..')
                    sys.exit()
                if self.reading(self.id, hex_password):
                    return
                if str(self.start_passwd)[3:] == '000':
                    print(' [Пауза 3 сек...]')
                    sleep(3)
                    self._check_test()
                # start_passwd += 2 if str(start_passwd)[5] == '9' else 1
                self.start_passwd += 1
        else:
            sys.exit()
