from typing import List
from config import config as cfg
from datetime import datetime
from common.modbus_crc16 import crc16
from common.colors import c
from common.uart import UartSerialPort
from decorators.repeat import Repeat, repeat


class ExchangeProtocol(UartSerialPort):

    def __init__(self):
        super().__init__()

    @repeat
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
