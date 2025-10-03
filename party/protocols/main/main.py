from config import PARTY_ID,N,t
from protocols.baseProtocol import BaseProtocol

class Main(BaseProtocol):
    @staticmethod
    def get_messages():
        return []

    @staticmethod
    def get_subprotocols():
        return ["bracha_0"]

    def __init__(self, manager, path, params):
        super().__init__(manager, path)
        self.start_subprotocol(f"bracha_0",params={"speaker":3,"value":b"myvalue"})

    def handle_message(self, message, by, data):
        pass

    def handle_subprotocol(self, subprotocol, index, result):
        print(f"subprotocol {subprotocol}_{index} returned with result:{result}")
        self.return_result(result)
