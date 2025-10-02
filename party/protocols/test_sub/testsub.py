from config import PARTY_ID,N,t
from protocols.baseProtocol import BaseProtocol

class TestSub(BaseProtocol):
    @staticmethod
    def get_messages():
        return ["dealer_msg", "response"]

    @staticmethod
    def get_subprotocols():
        return []

    def __init__(self, manager, path, params):
        super().__init__(manager, path)
        self.dealer = params["dealer"]
        self.responses = []

        if PARTY_ID == self.dealer:
            for i in range(N):
                if i != PARTY_ID:
                    self.send_message(i, "dealer_msg", {"value": 5})

    def handle_message(self, message, by, data):
        if message=="dealer_msg":
            if by == self.dealer:
                self.send_message(self.dealer, "response", {"value": b"6"})
                self.stop()
        elif message=="response":
            if data.get("value")==b"6":
                self.responses.append(by)
                print(f"{self.path}: handling {message} by {by}, responses:{self.responses}")
                if len(self.responses) >= 3*t:
                    self.return_result(self.responses)

    def handle_subprotocol(self, subprotocol, index, result):
        pass
