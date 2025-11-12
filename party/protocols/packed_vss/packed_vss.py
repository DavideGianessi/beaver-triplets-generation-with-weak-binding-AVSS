from config import PARTY_ID,N,t,p
import galois
from protocols.baseProtocol import BaseProtocol
from type_defs import BivariatePolynomial,UnivariatePolynomial
from .star import find_star,verify_star
from .reed_solomon import construct_polynomial
from util.logging import log

GF = galois.GF(p)

def gf_size(field):
    return (field.characteristic.bit_length() + 7) // 8

def gf_to_bytes(elem,field=GF):
    return int(elem).to_bytes(gf_size(field), "little")

def bytes_to_gf(b,field=GF):
    return field(int.from_bytes(b,"little"))

class PackedVSS(BaseProtocol):
    @staticmethod
    def get_messages():
        return ["shares","exchange","reconstruct"]

    @staticmethod
    def get_subprotocols(params):
        star_schema= {"type":"dict","keys": {
            "C":{"type": "list", "maxlen":N, "items": {"type": "int", "min": 1, "max": N}},
            "D":{"type": "list", "maxlen":N, "items": {"type": "int", "min": 1, "max": N}},
            "G":{"type": "list", "maxlen":N, "items": {"type": "int", "min": 1, "max": N}},
            "F":{"type": "list", "maxlen":N, "items": {"type": "int", "min": 1, "max": N}},
          }}
        empty= {"type":"bytes","len":0}
        return {"bracha_0": {"speaker":params["dealer"],"content_schema": star_schema}} | \
            {f"bracha_{i*(N+1)+i2}": {"speaker":i,"content_schema": empty} for i in range(1,N+1) for i2 in range(1,N+1) if i!=i2}

    @staticmethod
    def get_schema(message,by,params):
        if message=="shares" and by==params["dealer"]:
            return {"type": "list", "len": params["batching"], "items": {"type":"dict", "keys": {
                "fx": {"type": "bytes", "len": UnivariatePolynomial.get_size(t+t//2,GF) },
                "fy": {"type": "bytes", "len": UnivariatePolynomial.get_size(t,GF) },
                }}}
        if message=="exchange":
            return {"type": "list", "len": params["batching"], "items": {"type":"dict", "keys": {
                "fxi": {"type": "bytes", "len": gf_size(GF) },
                "fyi": {"type": "bytes", "len": gf_size(GF) },
                }}}
        if message=="reconstruct":
            return {"type": "list", "len": params["batching"], "items": 
                    {"type": "bytes", "len": gf_size(GF) },
                }
        return None


    def send_share_checks(self):
        for i in range(1,N+1):
            if i != PARTY_ID:
                exch=[]
                clearexch=[]
                for s in self.share:
                    exch.append({"fxi": gf_to_bytes(s["fx"](i)),"fyi": gf_to_bytes(s["fy"](i))})
                    clearexch.append({"fxi": s["fx"](i),"fyi": s["fy"](i)})
                #log(f"exchanging {clearexch} with {i}")
                self.send_message(i,"exchange",exch)


    def __init__(self, manager, path, params):
        super().__init__(manager, path)
        self.dealer = params["dealer"]
        self.batching = params["batching"]
        self.graph = [ [0] * (N+1) for _ in range(N+1)]
        self.share = None
        self.exchanges = {}
        self.others= {}
        self.reconstructions= {}
        self.star=None
        self.fixedF=False
        self.fixedG=False
        self.newshareg=[]
        self.newsharef=[]
        self.foundstar=False

        if PARTY_ID != self.dealer:
            self.start_subprotocol("bracha_0",params={"speaker":self.dealer})
        for i in range(1,N+1):
            if i != PARTY_ID:
                for i2 in range(1,N+1):
                    if i!=i2:
                        self.start_subprotocol(f"bracha_{i*(N+1)+i2}",params={"speaker":i})
        if PARTY_ID == self.dealer:
            Ses=params["input"]
            assert(isinstance(Ses,list))
            assert(len(Ses)==self.batching)
            for S in Ses:
                assert(isinstance(S,BivariatePolynomial))
                assert(S.degree_x==(t+t//2))
                assert(S.degree_y==t)
            for i in range(1,N+1):
                share=[]
                for S in Ses:
                    share.append({"fx":S.univariate_in_x(i).to_bytes(),"fy":S.univariate_in_y(i).to_bytes()})
                if i!=PARTY_ID:
                    self.send_message(i,"shares",share)
                else:
                    self.share=[{"fx":UnivariatePolynomial.from_bytes(s["fx"],GF,t+t//2),"fy":UnivariatePolynomial.from_bytes(s["fy"],GF,t)} for s in share]
                    self.send_share_checks()


    def handle_message(self, message, by, data):
        if message=="shares":
            if by == self.dealer:
                share=data
                self.share=[{"fx":UnivariatePolynomial.from_bytes(s["fx"],GF,t+t//2),"fy":UnivariatePolynomial.from_bytes(s["fy"],GF,t)} for s in share]
                self.send_share_checks()
                #log(f"share:{self.share}")
        elif message=="reconstruct":
            self.reconstructions[by]=[ bytes_to_gf(d) for d in data]
        elif message=="exchange":
            data=[{"fxi": bytes_to_gf(d["fxi"]),"fyi": bytes_to_gf(d["fyi"])} for d in data]
            self.exchanges[by]=data
            #log(f"received exchange {data} from {by}")
            self.others[by]=data
        if self.share and self.exchanges:
            for index,exch in self.exchanges.items():
                correct=True
                for i in range(self.batching):
                    if exch[i]["fxi"]!= self.share[i]["fy"](index) or exch[i]["fyi"]!= self.share[i]["fx"](index):
                        correct=False
                if correct:
                    self.start_subprotocol(f"bracha_{PARTY_ID*(N+1)+index}",params={"speaker":PARTY_ID, "value":b""})
            self.exchanges={}
        self.check_star()


    def handle_subprotocol(self, subprotocol, index, result):
        #log(f"new sub finished index: {index} ({index//(N+1)},{index%(N+1)})")
        if index!=0:
            i=index//(N+1)
            i2=index%(N+1)
            self.graph[i][i2]+=1
            self.graph[i2][i]+=1
            if self.graph[i][i2]==2:
                pass
                #log(f"new edge ({i},{i2})")
        else:
            self.star=[set(result["C"]),set(result["D"]),set(result["G"]),set(result["F"])]
            #log(f"star: {self.star}")
        if PARTY_ID==self.dealer:
            pass
            #log(f"graph: {self.graph}")
        if not self.foundstar and self.dealer == PARTY_ID:
            star = find_star(self.graph)
            #log(f"star?? {star}")
            if star:
                C,D,G,F=star
                C,D,G,F=list(C),list(D),list(G),list(F)
                self.start_subprotocol("bracha_0",params={"speaker":PARTY_ID, "value": {"C":C,"D":D,"G":G,"F":F}})
                self.foundstar=True
        self.check_star()

    def check_star(self):
        if self.star:
            C,D,G,F=self.star
            if verify_star(self.graph,C,D,G,F):
                if PARTY_ID not in G and not self.fixedG:
                    self.newshareg=[]
                    fixed=True
                    for i in range(self.batching):
                        points=[(GF(key),value[i]["fxi"]) for key,value in self.others.items() if key in F]
                        newsh=construct_polynomial(points,t,t,GF)
                        if newsh:
                            self.newshareg.append(newsh)
                        else:
                            fixed=False
                            break
                    if fixed:
                        self.fixedG=True
                        for i in range(1,N+1):
                            if i in F:
                                continue
                            if i==PARTY_ID:
                                self.reconstructions[i]=[ g(i) for g in self.newshareg ]
                            else:
                                self.send_message(i,"reconstruct",[ gf_to_bytes(g(i)) for g in self.newshareg ])
                if PARTY_ID not in F and not self.fixedF:
                    self.newsharef=[]
                    fixed=True
                    for i in range(self.batching):
                        points=[(GF(key),value[i]["fyi"]) for key,value in self.others.items() if key in G]
                        points+=[(GF(key),value[i]) for key,value in self.reconstructions.items() if key not in G]
                        newsh=construct_polynomial(points,t+t//2,t,GF)
                        if newsh:
                            self.newsharef.append(newsh)
                        else:
                            fixed=False
                            break
                    if fixed:
                        self.fixedF=True
                if (PARTY_ID in G or self.fixedG) and (PARTY_ID in F or self.fixedF):
                    if PARTY_ID in G:
                        self.newshareg=[self.share[i]["fy"] for i in range(self.batching)]
                    if PARTY_ID in F:
                        self.newsharef=[self.share[i]["fx"] for i in range(self.batching)]
                    self.share=[{"fx": self.newsharef[i],"fy": self.newshareg[i]} for i in range(self.batching)]
                    self.return_result(self.share)
                    self.stop()
                    return

