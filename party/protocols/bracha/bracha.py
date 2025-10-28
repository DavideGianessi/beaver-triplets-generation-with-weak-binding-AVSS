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

class Bracha(BaseProtocol):
    @staticmethod
    def get_messages():
        return ["init", "echo","ready"]

    @staticmethod
    def get_subprotocols():
        return []

    @staticmethod
    def get_schema(message,by,params):
        if message=="echo" or message=="ready":
            return {    "type": "dict",
                        "keys": {
                            "v": params["content_schema"],
                        },
                    }
        if message=="init" and (params.get("speaker")==by or "speaker" not in params):
            return {    "type": "dict",
                        "keys": {
                            "v": params["content_schema"],
                        },
                    }
        return None

    def __init__(self, manager, path, params):
        super().__init__(manager, path)
        self.speaker = params["speaker"]
        self.echos = []
        self.readys = []
        self.ireadied = False
        if PARTY_ID == self.speaker:
            self.iechoed=True
            self.echos.append((params["value"],1))
            for i in range(1,N+1):
                if i != PARTY_ID:
                    self.send_message(i, "init", {"v": params["value"]})
                    self.send_message(i, "echo", {"v": params["value"]})

    def handle_message(self, message, by, data):
        if message=="init" and by==self.speaker:
            self.value=data["v"]
            increment_counter(self.echos,data["v"]) #my implicit echo
            for i in range(1,N+1):
                if i!= PARTY_ID:
                    self.send_message(i, "echo", {"v": data["v"]})
        elif message=="echo":
            increment_counter(self.echos,data["v"])
        elif message=="ready":
            increment_counter(self.readys,data["v"])
        if not self.ireadied and (get_count(self.echos,data["v"])>=N-t or get_count(self.readys,data["v"])>=t+1):
            self.ireadied = True
            increment_counter(self.readys,data["v"]) #my implicit ready
            for i in range(1,N+1):
                if i!= PARTY_ID:
                    self.send_message(i, "ready", {"v": data["v"]})
        if get_count(self.readys, data["v"])>=2*t+1: #accept the value and terminate protocol
            self.return_result(data["v"])
            self.stop()

    def handle_subprotocol(self, subprotocol, index, result):
        pass
