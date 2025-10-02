from config import PARTY_ID,N,t
from protocols.baseProtocol import BaseProtocol

class TestProtocol(BaseProtocol):
    @staticmethod
    def get_messages():
        return []

    @staticmethod
    def get_subprotocols():
        return [f"testsub_{i}" for i in range(N)]

    def __init__(self, manager, path, params):
        super().__init__(manager, path)
        for i in range(N):
            self.start_subprotocol(f"testsub_{i}",params={"dealer":i})

    def handle_message(self, message, by, data):
        pass

    def handle_subprotocol(self, subprotocol, index, result):
        print(f"subprotocol {subprotocol}_{index} returned with result:{result}")
        if subprotocol=="testsub" and index==PARTY_ID:
           self.return_result(result)
