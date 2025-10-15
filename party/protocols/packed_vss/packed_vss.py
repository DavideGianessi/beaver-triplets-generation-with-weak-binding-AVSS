from config import PARTY_ID,N,t
from protocols.baseProtocol import BaseProtocol
from type_defs import BivariatePolynomial,UnivariatePolynomial
from star import find_star,verify_star
from reed_solomon import construct_polynomial

class PackedVSS(BaseProtocol):
    @staticmethod
    def get_messages():
        return ["shares","exchange","reconstruct"]

    @staticmethod
    def get_subprotocols():
        return ["bracha_0"]+[f"bracha_{i*N+i2}" for i in range(1,N+1) for i2 in range(1,N+1)]


    def send_share_checks(self):
        for i in range(1,N+1):
            if i != PARTY_ID:
                exch=[]
                for fx,fy in self.share:
                    exch.append([fx(i).tobytes(),fy(i).tobytes()]
                self.send_message(i,"exchange",exch)


    def __init__(self, manager, path, params):
        super().__init__(manager, path)
        self.dealer = params["dealer"]
        self.graph = [ [0] * (N+1) for _ in range(N+1)]
        self.share = []
        self.exchanges = {}
        self.othersG= {}
        self.othersF= {}
        self.reconstructions= {}
        self.star=None

        if PARTY_ID != self.dealer:
            self.start_subprotocol("bracha_0")
        for i in range(1,N+1):
            if i != PARTY_ID:
                for i2 in range(1,N+1):
                    self.start_subprotocol(f"bracha_{i*N+i2}",params={"speaker":i})
        if PARTY_ID == self.dealer:
            Ses=params["input"]
            assert(isinstance(Ses,list))
            assert(len(Ses)==N)
            for S in Ses:
                assert(isinstance(S,BivariatePolynomial))
                assert(S.degree_x==(t+t//2+1))
                assert(S.degree_y==t)
            for i in range(1,N+1):
                share=[]
                for S in Ses:
                    share.append([univariate_in_x(i).to_bytes(),univariate_in_y(i).to_bytes()])
                if i!=PARTY_ID:
                    self.send_message(i,"shares",share)
                else:
                    self.share=[[UnivariatePolynomial.from_bytes(s[0]),UnivariatePolynomial.from_bytes(s[1])] for s in share]
                    self.send_share_checks()


    def handle_message(self, message, by, data):
        if message=="shares":
            if by == self.dealer:
                share=data
                self.share=[[UnivariatePolynomial.from_bytes(s[0]),UnivariatePolynomial.from_bytes(s[1])] for s in share]
                if len(self.share) != N:
                    self.share=None
                    return
                for s in self.share:
                    if s[0].degree > (3*t)//2 or s[1].degree > t:
                        self.share=None
                        return
                if self.share:
                    self.send_share_checks()
        elif message=="exchange":
            self.exchanges[by]=data
            self.othersF[by]=data[0]
            self.othersG[by]=data[1]
        if len(self.share)>0 and self.exchanges:
            for index,exch in self.exchanges.items():
                correct=True
                for i in range(len(exch)):
                    if exch[0]!= self.share[i][1](index) or exch[1]!= self.share[i][0](index):
                        correct=False
                if correct:
                    self.start_subprotocol(f"bracha_{PARTY_ID*N+index}",params={"speaker":PARTY_ID, "value":b""})
            self.exchanges={}


    def handle_subprotocol(self, subprotocol, index, result):
        if index!=0:
            i=index//N
            i2=index%N
            self.graph[i][i2]+=1
            self.graph[i2][i]+=1
        else:
            if self.dealer != PARTY_ID:
                self.star=result
                self.stop_useless_edges()
        if not self.star and self.dealer == PARTY_ID:
            star = find_star(self.graph)
            if star:
                C,D,G,F=star
                C,D,G,F=list(C),list(D),list(G),list(F)
                self.start_subprotocol("bracha_0",params={"speaker":PARTY_ID, "value": [C,D,G,F]})
                self.stop_useless_edges()
                self.return_to_parent(self.share)
                self.stop()
                return
        if self.star:
            C,D,G,F=self.star
            if verify_star(self.graph,C,D,G,F):
                if PARTY_ID in G and PARTY_ID in F:
                    self.return_to_parent(self.share)
                    self.stop()
                    return
                
                    
            


