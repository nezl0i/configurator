# Connect MODE
CONNECT_MODE = 0  # 0-RS485, 1-CSD, 2-TCP/IP
REPEAT_COUNT = 3  # Количество повторов при неудачном ответе

# Debug MODE
DEBUG = True

# Serial port
UART_PORT = '/dev/ttyUSB0'  # /dev/ttyUSB0
UART_PORT_TIMEOUT = 0.9  # UART(0.048 - 0.5)

# TCP/IP
TCP_HOST = '127.0.0.1'
TCP_PORT = 1234
TCP_TIMEOUT = 5  # Timeout TCP(2-10)

# To BRUT_PASSWORD
START_PASSWORD = 000000
STOP_PASSWORD = 999999

# Device
DEVICE_ID = 0
DEVICE_LEVEL = 2
DEVICE_PASSWORD = '222222'
DEVICE_PASSWORD_MODE = 'hex'

# Update firmware
FIRMWARE_FILE = 'update/*.txt'
CLEAR_EVENTS_FILE = 'meters/*.json'
METERS_FILE = 'meters/*.json'

# CSD MODE
CSD_PHONE = '+12345678901'
CSD_TIMEOUT = 15
