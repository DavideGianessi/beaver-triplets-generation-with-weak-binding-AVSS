from abc import ABC, abstractmethod
from util.paths import make_protocol_path,make_message_path
from util.networking import send

class BaseProtocol(ABC):
    def __init__(self, manager, path):
        self.manager = manager
        self.path = path
        self.returned = False

    def start_subprotocol(self, full_name, params=None):
        subpath = make_protocol_path(self.path,full_name)
        self.manager.start_protocol(subpath, params=params)

    def stop(self):
        self.manager.stop_protocol(self.path)

    def stop_subprotocol(self, full_name):
        subpath = make_protocol_path(self.path,full_name)
        self.manager.stop_protocol(subpath)

    def return_result(self, result):
        if self.returned:
            raise Exception("you have already returned from this protocol")
        self.returned = True
        self.manager.return_to_parent(self.path, result)

    def send_message(self, to, message_name, data):
        messageid = make_message_path(self.path,message_name)
        send(to, messageid, data)

    @staticmethod
    @abstractmethod
    def get_messages():
        ...

    @staticmethod
    @abstractmethod
    def get_subprotocols():
        ...

    @abstractmethod
    def handle_message(self, message, by, data):
        ...

    @abstractmethod
    def handle_subprotocol(self, subprotocol, index, result):
        ...
