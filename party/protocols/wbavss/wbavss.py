from config import PARTY_ID,N,t,p
import galois
from protocols.baseProtocol import BaseProtocol
from type_defs import TrivariatePolynomial,BivariatePolynomial,UnivariatePolynomial
from .bigstar import find_dense_or_bigstar,verify_dense_or_bigstar
from .external_validity import external_validity
from .linear_circuit import linear_to_bivariate,linear_to_univariate
from util.logging import log

GF = galois.GF(p)

def check_my_share(share):
    for s in share:
        exch=[]
        tLiQi=UnivariatePolynomial([0],GF)
        for j in range(0,12,3):
            exch.append(s[j].univariate_in_x(PARTY_ID))
            exch.append(s[j].univariate_in_y(PARTY_ID))
            exch.append(s[j+1].univariate_in_x(PARTY_ID))
            exch.append(s[j+1].univariate_in_y(PARTY_ID))
            exch.append(s[j+2].univariate_in_x(PARTY_ID))
            exch.append(s[j+2].univariate_in_y(PARTY_ID))
            tLiQi+= pow(PARTY_ID,(j//3)*(t//2),p) * linear_to_univariate(PARTY_ID,s[j],GF)
        exch.append(tLiQi)
        if not consistent(PARTY_ID,s,exch):
            return False
    return True

def consistent(j,share,exch):
    #log(f"comparing----\n{share=}\n{exch=}\n")
    T=share[12]
    for r in range(4):
        Q,W,R=share[r*3:(r+1)*3]
        if (exch[r*6]!=W.univariate_in_x(j) or
            exch[r*6+1]!=R.univariate_in_x(j) or
            exch[r*6+2]!=Q.univariate_in_x(j) or
            exch[r*6+3]!=R.univariate_in_y(j) or
            exch[r*6+4]!=Q.univariate_in_y(j) or
            exch[r*6+5]!=W.univariate_in_y(j)):
            #log("failed linearity checks ########")
            return False
    if exch[24]!=T.univariate_in_x(j):
        #log("failed circuit check ########")
        return False
    #log("success ########")
    return True
            

class WBAVSS(BaseProtocol):
    @staticmethod
    def get_messages():
        return ["shares","exchange"]

    @staticmethod
    def get_subprotocols(params):
        bigstar_schema= {"type":"dict","keys": {
            "kind": {"type": "str", "regex": r"dense|bigstar"},
            "C":{"type": "list", "maxlen":N, "items": {"type": "int", "min": 1, "max": N}},
            "D":{"type": "list", "maxlen":N, "items": {"type": "int", "min": 1, "max": N}},
          }}
        empty= {"type":"bytes","len":0}
        return {"bracha_0": {"speaker":params["dealer"],"content_schema": bigstar_schema}} | \
            {f"bracha_lite_{i*(N+1)+i2}": {"speaker":i} for i in range(1,N+1) for i2 in range(1,N+1) if i!=i2}

    @staticmethod
    def get_schema(message,by,params):
        if message=="shares" and by==params["dealer"]:
            return {"type": "list", "len": params["batching"], "items": 
                    {"type":"list", "len":13, "items": 
                        {"type": "bytes", "len": BivariatePolynomial.get_size(t+t//2,t+t//2,GF) }
                     }
                    }
        if message=="exchange":
            return {"type": "list", "len": params["batching"], "items": 
                    {"type":"list", "len":25, "items": 
                        {"type": "bytes", "len": UnivariatePolynomial.get_size(t+t//2,GF) }
                     }
                    }
        return None


    def send_share_checks(self):
        for i in range(1,N+1):
            if i != PARTY_ID:
                exch=[]
                for s in self.share:
                    this_exch=[]
                    tLjQi=UnivariatePolynomial([0],GF)
                    for j in range(0,12,3):
                        this_exch.append(s[j].univariate_in_x(i))
                        this_exch.append(s[j].univariate_in_y(i))
                        this_exch.append(s[j+1].univariate_in_x(i))
                        this_exch.append(s[j+1].univariate_in_y(i))
                        this_exch.append(s[j+2].univariate_in_x(i))
                        this_exch.append(s[j+2].univariate_in_y(i))
                        tLjQi+= pow(i,(j//3)*(t//2),p) * linear_to_univariate(i,s[j],GF)
                    this_exch.append(tLjQi)
                    exch.append(this_exch)
                #log(f"exchanging {exch} with {i}")
                exch=[[univ.to_bytes() for univ in this_exch] for this_exch in exch]
                self.send_message(i,"exchange",exch)


    def __init__(self, manager, path, params):
        super().__init__(manager, path)
        self.dealer = params["dealer"]
        self.batching = params["batching"]
        self.graph = [ [0] * (N+1) for _ in range(N+1)]
        self.share = None
        self.exchanges = {}
        self.star=None
        self.foundstar=False

        if PARTY_ID != self.dealer:
            self.start_subprotocol("bracha_0",params={"speaker":self.dealer})
            self.externalA=params["externalA"]
            self.externalB=params["externalB"]
            self.externalC=params["externalC"]
        for i in range(1,N+1):
            if i != PARTY_ID:
                for i2 in range(1,N+1):
                    if i!=i2:
                        self.start_subprotocol(f"bracha_lite_{i*(N+1)+i2}",params={"speaker":i})
        if PARTY_ID == self.dealer:
            Ses=params["input"]
            assert(isinstance(Ses,list))
            assert(len(Ses)==self.batching)
            for Ss in Ses:
                assert(isinstance(Ss,list))
                assert(len(Ss)==4)
                for S in Ss:
                    assert(isinstance(S,TrivariatePolynomial))
                    assert(S.degree_x==(t+t//2))
                    assert(S.degree_y==(t+t//2))
                    assert(S.degree_z==(t+t//2))
            for i in range(1,N+1):
                share=[]
                for Ss in Ses:
                    this_share=[]
                    for S in Ss:
                        this_share.append(S.bivariate_in_xy(i).to_bytes())    # Qi(x,y)
                        this_share.append(S.bivariate_in_xz(i).to_bytes())    # Wi(x,z)
                        this_share.append(S.bivariate_in_yz(i).to_bytes())    # Ri(y,z)
                    this_share.append(linear_to_bivariate(i,Ss,GF).to_bytes()) # Ti(x,z)
                    share.append(this_share)
                if i!=PARTY_ID:
                    self.send_message(i,"shares",share)
                else:
                    self.share=[[BivariatePolynomial.from_bytes(s,GF,t+t//2,t+t//2) for s in ss] for ss in share]
                    #log(f"share:{self.share}")
                    self.send_share_checks()


    def handle_message(self, message, by, data):
        if message=="shares":
            if by == self.dealer:
                share=data
                share=[[BivariatePolynomial.from_bytes(s,GF,t+t//2,t+t//2) for s in ss] for ss in share]
                #log(f"{check_my_share(share)=}")
                if all([external_validity(self.externalA[i],self.externalB[i],self.externalC[i],share[i][12],PARTY_ID,GF) for i in range(self.batching)]) and check_my_share(share):
                    self.share=share
                    self.send_share_checks()
                    #log(f"share:{self.share}")
        elif message=="exchange":
            data=[[UnivariatePolynomial.from_bytes(d,GF,t+t//2) for d in dd] for dd in data]
            self.exchanges[by]=data
            #log(f"received exchange {data} from {by}")
        if self.share and self.exchanges:
            for index,exch in self.exchanges.items():
                correct=True
                for i in range(self.batching):
                    if not consistent(index,self.share[i],exch[i]):
                        correct=False
                if correct:
                    self.start_subprotocol(f"bracha_lite_{PARTY_ID*(N+1)+index}",params={"speaker":PARTY_ID, "value":b""})
            self.exchanges={}
        self.check_star()


    def handle_subprotocol(self, subprotocol, index, result):
        if index!=0:
            i=index//(N+1)
            i2=index%(N+1)
            self.graph[i][i2]+=1
            self.graph[i2][i]+=1
            if self.graph[i][i2]==2:
                #log(f"new edge ({i},{i2})")
                pass
        else:
            self.startype=result["kind"]
            self.star=[set(result["C"]),set(result["D"])]
            #log(f"startype: {self.startype}")
            #log(f"star: {self.star}")
        if PARTY_ID==self.dealer:
            #log(f"graph: {self.graph}")
            pass
        if not self.foundstar and self.dealer == PARTY_ID:
            star = find_dense_or_bigstar(self.graph)
            #log(f"star?? {star}")
            if star:
                kind,C,D=star
                C,D=list(C),list(D)
                self.start_subprotocol("bracha_0",params={"speaker":PARTY_ID, "value": {"kind":kind,"C":C,"D":D}})
                self.foundstar=True
        self.check_star()

    def check_star(self):
        if self.star:
            C,D=self.star
            if verify_dense_or_bigstar(self.graph,self.startype,C,D):
                self.return_result(True)
                self.stop()
                return

