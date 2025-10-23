from config import PARTY_ID,N,t
from protocols.baseProtocol import BaseProtocol

class TestSub(BaseProtocol):
    @staticmethod
    def get_messages():
        return ["dealer_msg", "response"]

    @staticmethod
    def get_subprotocols(params):
        return {}

    @staticmethod
    def get_schema(message,by,params):
        if params["dealer"]==PARTY_ID and message="response":
            return {    "type": "dict",
                        "keys": {
                        "value": {"type": "bytes", "len": 1}
                        },
                    }
        if params["dealer"]==by and message="dealer_msg" :
            return {    "type": "dict",
                        "keys": {
                        "value": {"type": "bytes", "len": 1}
                        },
                    }
        return None

    def __init__(self, manager, path, params):
        super().__init__(manager, path)
        self.dealer = params["dealer"]
        self.responses = []

        if PARTY_ID == self.dealer:
            for i in range(1,N+1):
                if i != PARTY_ID:
                    self.send_message(i, "dealer_msg", {"value": b"5"})

    def handle_message(self, message, by, data):
        if message=="dealer_msg" and by==self.dealer:
            self.send_message(self.dealer, "response", {"value": b"6"})
            self.stop()
        elif message=="response":
            if data.get("value")==b"6":
                self.responses.append(by)
                print(f"{self.path}: handling {message} by {by}, responses:{self.responses}")
                if len(self.responses) >= 3*t:
                    self.return_result(self.responses)
                    self.stop()

    def handle_subprotocol(self, subprotocol, index, result):
        pass
