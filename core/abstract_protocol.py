import abc
from core.build_channel import ExchangeProtocol


class AbstractIncotexProtocol(metaclass=abc.ABCMeta):
    def __init__(self):
        self.exchange = ExchangeProtocol().exchange
        self.status = False
