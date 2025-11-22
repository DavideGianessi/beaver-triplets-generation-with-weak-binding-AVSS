from config import PARTY_ID,N,t
from protocols.baseProtocol import BaseProtocol

def increment_counter(counter_list, value):
    for i, (v, count) in enumerate(counter_list):
        if v == value:
            counter_list[i] = (v, count + 1)
            return
    counter_list.append((value, 1))

def get_count(counter_list, value):
    for v, count in counter_list:
        if v == value:
            return count
    return 0

class BrachaLite(BaseProtocol):
    @staticmethod
    def get_messages():
        return ["init", "ready"]

    @staticmethod
    def get_subprotocols():
        return []

    @staticmethod
    def get_schema(message,by,params):
        if message=="ready":
            return {"type": "bytes", "len": 0 }
        if message=="init" and (params.get("speaker")==by or "speaker" not in params):
            return {"type": "bytes", "len": 0 }
        return None

    def __init__(self, manager, path, params):
        super().__init__(manager, path)
        self.speaker = params["speaker"]
        self.readys = 0
        self.ireadied = False
        if PARTY_ID == self.speaker:
            self.ireadied=True
            self.readys+=1
            for i in range(1,N+1):
                if i != PARTY_ID:
                    self.send_message(i, "init", b"")
                    self.send_message(i, "ready", b"")

    def handle_message(self, message, by, data):
        if message=="init" and by==self.speaker:
            self.ireadied = True
            self.readys+=1
            for i in range(1,N+1):
                if i!= PARTY_ID:
                    self.send_message(i, "ready", b"")
        elif message=="ready":
            self.readys+=1
        if not self.ireadied and self.readys>=t+1:
            self.ireadied = True
            self.readys+=1
            for i in range(1,N+1):
                if i!= PARTY_ID:
                    self.send_message(i, "ready", b"")
        if self.readys>=2*t+1: #accept the value and terminate protocol
            self.return_result(b"")
            self.stop()

    def handle_subprotocol(self, subprotocol, index, result):
        pass
