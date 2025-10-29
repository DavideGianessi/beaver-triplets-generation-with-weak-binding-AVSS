from config import PARTY_ID,N,t,p
from protocols.baseProtocol import BaseProtocol
from util.logging import log
import galois
from type_defs import BivariatePolynomial

GF=galois.GF(p)

class Main(BaseProtocol):
    @staticmethod
    def get_messages():
        return []

    @staticmethod
    def get_subprotocols(params):
        return {"packed_vss_0": {"dealer": 3,"batching":2}}

    @staticmethod
    def get_schema(message,by,params):
        return None

    def __init__(self, manager, path, params):
        super().__init__(manager, path)
        if PARTY_ID==3:
            coeffs = [ [x*100+y for y in range(t+1)] for x in range(t+t//2+1)]
            S1=BivariatePolynomial(coeffs, GF)
            coeffs = [ [x*1000+y for y in range(t+1)] for x in range(t+t//2+1)]
            S2=BivariatePolynomial(coeffs, GF)
            print(f"input: [{S1},{S2}]")
            log(f"input: [{S1},{S2}]")
            self.start_subprotocol(f"packed_vss_0",params={"dealer":3,"batching":2,"input":[S1,S2]})
        else:
            self.start_subprotocol(f"packed_vss_0",params={"dealer":3,"batching":2})

    def handle_message(self, message, by, data):
        pass

    def handle_subprotocol(self, subprotocol, index, result):
        print(f"subprotocol {subprotocol}_{index} returned with result:{result}")
        self.return_result(result)
