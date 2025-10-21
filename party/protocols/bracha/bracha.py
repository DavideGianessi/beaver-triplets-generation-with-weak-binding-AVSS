from config import PARTY_ID,N,t
from protocols.baseProtocol import BaseProtocol

class Bracha(BaseProtocol):
    @staticmethod
    def get_messages():
        return ["init", "echo","ready"]

    @staticmethod
    def get_subprotocols():
        return []

    @staticmethod
    def get_schema(message,by,params):
        if message=="init" and params["speaker"]==by:
            return {    "type": "dict",
                        "keys": {
                            "v": params["content_schema"],
                        },
                    }
        if message=="echo" or message=="ready":
            return {    "type": "dict",
                        "keys": {
                            "v": params["content_schema"],
                        },
                    }
        return None

    def __init__(self, manager, path, params):
        super().__init__(manager, path)
        self.speaker = params["speaker"]
        self.echos = {}
        self.readys = {}
        self.ireadied = False
        if PARTY_ID == self.speaker:
            self.iechoed=True
            self.echos[params["value"]]=1
            for i in range(1,N+1):
                if i != PARTY_ID:
                    self.send_message(i, "init", {"v": params["value"]})
                    self.send_message(i, "echo", {"v": params["value"]})

    def handle_message(self, message, by, data):
        if message=="init":
            self.value=data["v"]
            self.echos[data["v"]] = self.echos.get(data["v"],0)+1 # my implicit echo
            for i in range(1,N+1):
                if i!= PARTY_ID:
                    self.send_message(i, "echo", {"v": data["v"]})
        elif message=="echo":
            self.echos[data["v"]] = self.echos.get(data["v"],0)+1
        elif message=="ready":
            self.readys[data["v"]] = self.readys.get(data["v"],0)+1
        if not self.ireadied and (self.echos.get(data["v"],0)>=N-t or self.readys.get(data["v"],0)>=t+1):
            self.ireadied = True
            self.readys[data["v"]] = self.readys.get(data["v"],0)+1 #my implicit ready
            for i in range(1,N+1):
                if i!= PARTY_ID:
                    self.send_message(i, "ready", {"v": data["v"]})
        if self.readys.get(data["v"],0)>=2*t+1: #accept the value and terminate protocol
            self.return_result(data["v"])
            self.stop()

    def handle_subprotocol(self, subprotocol, index, result):
        pass
