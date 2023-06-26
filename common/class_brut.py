import os
import sys
from datetime import datetime
from time import sleep
from sys import platform
from config import config as cfg
from common.modbus_crc16 import crc16
from core.build_channel import ExchangeProtocol

try:
    from progress.bar import IncrementalBar
except ImportError:
    if platform.startswith('win'):
        os.system('py -m pip install progress')
    else:
        os.system('python3 -m pip install progress')
    from progress.bar import IncrementalBar

EP = ExchangeProtocol()


class Brutforce:
    def __init__(self):
        super().__init__()

        self.id = format(cfg.DEVICE_ID, '02X')

        self.start_passwd = cfg.START_PASSWORD
        self.stop_passwd = cfg.STOP_PASSWORD
        self.pass_mode = cfg.DEVICE_PASSWORD_MODE

        self.flag = False

        self.bar = IncrementalBar('Выполнение', max=self.stop_passwd - self.start_passwd)
        self._check_test()

    @staticmethod
    def __test(pk):
        test = f'{pk} 00 '
        transfer = bytearray.fromhex(test + crc16(bytearray.fromhex(test)))
        sys.stdout.write(f'Тест канала связи ...\r')
        if EP.mode == 2:
            EP.s.send(transfer)
            buffer = EP.s.recv(4)
        else:
            EP.set_timeout(EP.timeout)
            EP.sp.write(transfer)
            buffer = EP.sp.read(4)
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

    def reading(self, pk, input_pass=None):
        test = f'{pk} 01 02 {input_pass} '
        transfer = bytearray.fromhex(test + crc16(bytearray.fromhex(test)))
        sys.stdout.write(f' [Пробуем пароль - {input_pass}]\r')
        self.bar.next()
        if EP.mode == 2:
            EP.s.send(transfer)
            try:
                buffer = EP.s.recv(4)
            except TimeoutError:
                return False
        else:
            if EP.mode == 1:
                EP.set_timeout(1)
            EP.sp.write(transfer)
            buffer = EP.sp.read(4)

        while buffer:
            current_time = datetime.strftime(datetime.now(), '%Y-%m-%d_%H:%M:%S')
            print(f"Ответ от устройства >> {buffer.hex(' ', -1)}\n")
            print(f'Пароль найден - {input_pass}')
            with open(f'log/password/passwd_{current_time}.txt', 'w') as f:
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
