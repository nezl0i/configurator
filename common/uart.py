import sys
import serial
import serial.tools.list_ports
from config import config as cfg
from serial.serialutil import SerialException


# sudo nano /etc/udev/rules.d/50-myusb.rules
# KERNEL=="ttyUSB[0-9]*",MODE="0666"
# KERNEL=="ttyACM[0-9]*",MODE="0666"


class UartSerialPort:
    def __init__(self):
        self.timeout = 0.5
        self.mode = cfg.CONNECT_MODE

        if self.mode == 2:
            return
        else:
            if self.mode == 1:
                self.timeout = cfg.CSD_TIMEOUT
            elif self.mode == 0:
                self.timeout = cfg.UART_PORT_TIMEOUT
            self.list_port()
            try:
                self.sp = serial.Serial(
                    port=cfg.UART_PORT,
                    baudrate=9600,
                    parity=serial.PARITY_NONE,
                    stopbits=serial.STOPBITS_ONE,
                    bytesize=serial.EIGHTBITS,
                    timeout=self.timeout
                )
            except SerialException:
                print(f'Port {cfg.UART_PORT} not opened or port no available.')
                self.sp = None
                sys.exit()

            self.data = ''

    def __str__(self):
        return f'Port {self.sp.port} open' if self.sp else 'Port not opened or port no available'

    @staticmethod
    def list_port():
        ports = [port for port in serial.tools.list_ports.comports()]
        print('=' * 28, 'Default ports', '=' * 28)
        for port in ports:
            print(f'{port}')
        print('=' * 71, '\n')

    def set_timeout(self, val):
        self.sp.timeout = val

    def clear(self):
        self.sp.flushInput()
        self.sp.flushOutput()
