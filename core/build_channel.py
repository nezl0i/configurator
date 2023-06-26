import sys
import socket
from typing import List
from common.colors import c
from datetime import datetime
from config import config as cfg
from common.modbus_crc16 import crc16
from common.uart import UartSerialPort
from decorators.singleton import singleton
from decorators.repeat import repeat, multi_repeat


@singleton
class ExchangeProtocol(UartSerialPort):

    def __init__(self):
        super().__init__()

        self.phone = cfg.CSD_PHONE
        self.call_flag = False

        self.TCP_PORT = cfg.TCP_PORT
        self.TCP_HOST = cfg.TCP_HOST
        self.TCP_TIMEOUT = cfg.TCP_TIMEOUT
        self.s = None

        self.init()

    def init(self):
        if self.mode == 1:
            self.csd_connect()
        if self.mode == 2:
            self.socket_connect()

    def csd_connect(self):
        _CALL = {
            'AT': 'AT\r',
            'CBST': 'AT+CBST=71,0,1\r',
            'CALL': f'ATD{self.phone}\r'
        }
        self.set_timeout(.1)
        print(self.CSD_send(_CALL['AT']))
        print(self.CSD_send(_CALL['CBST']))
        self.set_timeout(self.timeout)
        for _ in range(3):
            calling = self.CSD_send(_CALL['CALL'])
            print(calling)
            if calling == 'Connect OK (9600)\n':
                self.call_flag = True
                break
        if self.call_flag:
            self.set_timeout(self.timeout // 6)
            return
        else:
            sys.exit()

    #   =========== From CSD terminal settings ================

    def CSD_send(self, string):
        send_string = bytearray(string, encoding='ascii')
        self.sp.write(send_string)
        print(f'Send command: {send_string.decode()}')
        self.data = self.CSD_read()
        return self.data

    def CSD_read(self):
        self.data = self.sp.readall()
        if 'OK' in self.data.decode():
            return 'OK'
        elif 'CONNECT' in self.data.decode():
            return 'Connect OK (9600)\n'
        elif 'BUSY' in self.data.decode():
            return 'BUSY\n'
        return 'ERROR\n'

    def socket_connect(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print('Socket successfully created')
        except socket.error as e:
            print(f'Socket creation failed with error as {e}')

        try:
            self.s.settimeout(self.TCP_TIMEOUT)
            print(f'Connection with {self.TCP_HOST}:{self.TCP_PORT} ...')
            self.s.connect((self.TCP_HOST, self.TCP_PORT))
            print(f'Connection OK.')
        except socket.error as err:
            print(err)
            sys.exit()

    @multi_repeat(repeat)
    # @repeat
    def exchange(self, command: List[str], count: int, param='', debug=cfg.DEBUG) -> tuple:
        current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
        buffer = None
        request = command[:]
        if param:
            request.append(param)
        data = ' '.join(request)
        transfer = bytearray.fromhex(data + ' ' + crc16(bytearray.fromhex(data)))
        print_line = ' '.join(map(lambda x: format(x, '02x'), transfer))

        if debug:
            print(f'[{current_time}] :{c.BLUE} >>', print_line, c.END)

        if self.mode != 2:
            self.sp.write(transfer)
            buffer = self.sp.read(count)
        else:
            try:
                self.s.sendall(transfer)
                buffer = self.s.recv(count)
            except socket.error:
                pass

        while buffer:
            if len(buffer) == count:
                return True, buffer.hex(' ', -1).split()
            return False, buffer.hex(' ', -1).split()
        return False, buffer
