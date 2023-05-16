import abc
from common.enum_command import ICommand
from common.attribute import IAttribute
from core.protocol import protocol


class DeviceDirector:
    def __init__(self):
        self._builder = None

    def construct(self, builder):
        self._builder = builder
        self._builder._test_channel()
        self._builder._authorization()
        self._builder._get_identifier()
        self._builder._check_connect()
        self._builder._get_serial_number()
        self._builder._get_execution()


class AbstractConnectDevice(metaclass=abc.ABCMeta):
    def __init__(self):
        self.command = ICommand()
        self.IA = IAttribute()
        self.command.set_id(self.IA.DEVICE_ID)
        self.command.OPEN_SESSION.append(self.IA.DEVICE_LEVEL)
        self.command.OPEN_SESSION.append(self.IA.DEVICE_PASSWORD)

    @abc.abstractmethod
    def _test_channel(self):
        pass

    @abc.abstractmethod
    def _authorization(self):
        pass

    @abc.abstractmethod
    def _get_identifier(self):
        pass

    @abc.abstractmethod
    def _check_connect(self):
        pass

    @abc.abstractmethod
    def _get_serial_number(self):
        pass

    @abc.abstractmethod
    def _get_execution(self):
        pass


class ConnectDevice(AbstractConnectDevice):

    def _test_channel(self):
        protocol.test_channel(self.command.TEST)

    def _authorization(self):
        protocol.open_session(self.command.OPEN_SESSION)
        self.status = True

    def _get_identifier(self):
        device_id = protocol.get_identifier(self.command.GET_IDENTIFIER)
        self.IA.DEVICE_ID = device_id

    def _check_connect(self):
        self.command.replace_id(self.IA.DEVICE_ID)
        protocol.open_session(self.command.OPEN_SESSION)

    def _get_serial_number(self):
        self.IA.DEVICE_SERIAL_NUMBER, self.IA.DEVICE_WORK_DATA = protocol.get_serial_number(self.command.GET_SERIAL)

    def _get_execution(self):
        variant_execution = protocol.get_execution(self.command.GET_EXECUTION)
        self.IA.DEVICE_VERSION, self.IA.DEVICE_REVISION, self.IA.DEVICE_CRC, self.IA.DEVICE_IMPULSE = variant_execution


device = ConnectDevice()
director = DeviceDirector()
# director.construct(device)
