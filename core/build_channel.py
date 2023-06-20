import sys
from typing import List
from config import config as cfg
from datetime import datetime
from common.modbus_crc16 import crc16
from common.colors import c
from common.uart import UartSerialPort
from decorators.repeat import Repeat, repeat, multi_repeat


class ExchangeProtocol(UartSerialPort):

    def __init__(self):
        super().__init__()
        self.mode = cfg.CONNECT_MODE
        self.phone = cfg.CSD_PHONE
        self.call_flag = False

        self.init()

    def init(self):
        if self.mode == 1:
            self.csd_connect()
        # if self.mode == 2:
        #     self.socket_connect()

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
            self.set_timeout(2)
            return
        else:
            sys.exit()

    @multi_repeat(repeat)
    # @repeat
    def exchange(self, command: List[str], count: int, param='') -> tuple:
        current_time = datetime.now().strftime('%d.%m.%Y %H:%M:%S.%f')
        request = command[:]
        if param:
            request.append(param)
        data = ' '.join(request)
        transfer = bytearray.fromhex(data + ' ' + crc16(bytearray.fromhex(data)))
        print_line = ' '.join(map(lambda x: format(x, '02x'), transfer))

        if cfg.DEBUG:
            print(f'[{current_time}] :{c.BLUE} >>', print_line, c.END)

        self.sp.write(transfer)
        buffer = self.sp.read(count)

        while buffer:
            if len(buffer) == count:
                return True, buffer.hex(' ', -1).split()
            return False, buffer.hex(' ', -1).split()
        return False, buffer
