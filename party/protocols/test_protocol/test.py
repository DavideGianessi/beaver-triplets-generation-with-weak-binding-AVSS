from config import PARTY_ID,N,t
from protocols.baseProtocol import BaseProtocol

class TestProtocol(BaseProtocol):
    @staticmethod
    def get_messages():
        return []

    @staticmethod
    def get_subprotocols(params):
        subs={}
        for i in range(1,N+1):
            subs[f"testsub_{i}"]={"dealer":i}
        return subs

    @staticmethod
    def get_schema(message,by,params):
        return None

    def __init__(self, manager, path, params):
        super().__init__(manager, path)
        for i in range(1,N+1):
            self.start_subprotocol(f"testsub_{i}",params={"dealer":i})

    def handle_message(self, message, by, data):
        pass

    def handle_subprotocol(self, subprotocol, index, result):
        print(f"subprotocol {subprotocol}_{index} returned with result:{result}")
        if subprotocol=="testsub" and index==PARTY_ID:
           self.return_result(result)
