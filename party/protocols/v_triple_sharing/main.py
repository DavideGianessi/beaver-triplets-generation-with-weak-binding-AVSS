from config import PARTY_ID,N,t,p,amount
from protocols.baseProtocol import BaseProtocol
from util.logging import log
import galois
from type_defs import UnivariatePolynomial,BivariatePolynomial,TrivariatePolynomial
from secrets import randbelow
from math import ceil
from .interpolation import lagrange_interpolate_univariate,interpolate_trivariate_from_grid

GF=galois.GF(p)

def rand_element(GF):
    order = int(GF.order)
    r=randbelow(order)
    return GF(r)

triples_per_instance=(t//2+1)**2
verification_batching=ceil(amount/triples_per_instance)
sharing_batching=verification_batches*3*(t//2+1)
real_amount=verification_batching*triples_per_instance

def lift_to_bivariate(U: UnivariatePolynomial, deg_y: int, field: type[galois.FieldArray]):
    n = U.degree
    coeffs = []
    for i in range(n + 1):
        row = [int(U.coeffs[i])]
        for j in range(1, deg_y + 1):
            row.append(int(rand_element(field)))
        coeffs.append(row)
    return BivariatePolynomial(coeffs, field)

class Main(BaseProtocol):
    @staticmethod
    def get_messages():
        return []

    @staticmethod
    def get_subprotocols(params):
        return {"packed_vss_0": {"dealer": 3,"batching":sharing_batching}, "wbavss_0": {"dealer": 3,"batching":verification_batching}}

    @staticmethod
    def get_schema(message,by,params):
        return None

    def __init__(self, manager, path, params):
        super().__init__(manager, path)
        if PARTY_ID==3:
            self.beaver_a = [rand_element(GF) for _ in range(real_amount)]
            self.beaver_b = [rand_element(GF) for _ in range(real_amount)]
            self.beaver_c = [beaver_a[i]*beaver_b[i] for i in range(real_amount)]
            As=[]
            Bs=[]
            Cs=[]
            for block in range(0,real_amount,t//2+1):
                pointsA=[]
                pointsB=[]
                pointsC=[]
                for beta in range(t//2+1):
                    pointsA.append((-beta,self.beaver_a[block+beta]))
                    pointsB.append((-beta,self.beaver_b[block+beta]))
                    pointsC.append((-beta,self.beaver_c[block+beta]))
                for i in range(t):
                    pointsA.append((1+i,rand_element(GF)))
                    pointsB.append((1+i,rand_element(GF)))
                    pointsC.append((1+i,rand_element(GF)))
                As.append(lift_to_bivariate(lagrange_interpolate_univariate(pointsA,GF),t,GF))
                Bs.append(lift_to_bivariate(lagrange_interpolate_univariate(pointsB,GF),t,GF))
                Cs.append(lift_to_bivariate(lagrange_interpolate_univariate(pointsC,GF),t,GF))
            self.start_subprotocol(f"packed_vss_0",params={"dealer":3,"batching":sharing_batching,"input":As+Bs+Cs})
            Ses=[]
            for block in range(0,len(As),t//2+1):
                S1points=[[[rand_element(GF) for z in range(t+t//2+1)] for y in range(t+t//2+1)] for z in range(t+t//2+1)]
                S2points=[[[rand_element(GF) for z in range(t+t//2+1)] for y in range(t+t//2+1)] for z in range(t+t//2+1)]
                S3points=[[[rand_element(GF) for z in range(t+t//2+1)] for y in range(t+t//2+1)] for z in range(t+t//2+1)]
                S4points=[[[rand_element(GF) for z in range(t+t//2+1)] for y in range(t+t//2+1)] for z in range(t+t//2+1)]
                for u in range(t//2+1):
                    for beta in range(t//2+1):
                        thisA=As[block+u].univariate_in_x(-beta)
                        thisB=Bs[block+u].univariate_in_x(-beta)
                        thisC=Cs[block+u].univariate_in_x(-beta)
                        thisE=thisA*ThisB-thisC
                        for k in range(1,t//2+1):
                            s1points[beta,k,u]=thisE.coeff[k]
                            s2points[beta,k,u]=thisE.coeff[t//2+k]
                            s3points[beta,k,u]=thisE.coeff[t+k]
                            s4points[beta,k,u]=thisE.coeff[t+t//2+k]
                S1=interpolate_trivariate_from_grid(S1points,GF)
                S2=interpolate_trivariate_from_grid(S2points,GF)
                S3=interpolate_trivariate_from_grid(S3points,GF)
                S4=interpolate_trivariate_from_grid(S4points,GF)
                Ses.append([S1,S2,S3,S4])
            self.start_subprotocol(f"wbavss_0",params={"dealer":3,"batching":verification_batching,"input":Ses})
        else:
            self.start_subprotocol(f"packed_vss_0",params={"dealer":3,"batching":sharing_batching})

    def handle_message(self, message, by, data):
        pass

    def handle_subprotocol(self, subprotocol, index, result):
        print(f"subprotocol {subprotocol}_{index} returned with result:{result}")
        if subprotocol=="packed_vss":
            blocksize=len(result)//3
            As=[r["fx"] for r in result[:blocksize]]
            Bs=[r["fx"] for r in result[blocksize:2*blocksize]]
            Cs=[r["fx"] for r in result[2*blocksize:]]
            self.a_shares=[]
            self.b_shares=[]
            self.c_shares=[]
            for i in range(blocksize):
                for beta in range(t//2+1):
                    self.a_shares.append(Aa[i](-beta))
                    self.b_shares.append(Ba[i](-beta))
                    self.c_shares.append(Ca[i](-beta))
            ext_a=[]
            ext_b=[]
            ext_c=[]
            for inst in range(0,len(self.a_shares),(t//2+1)**2):
                this_a=[]
                this_b=[]
                this_c=[]
                for u in range(0,(t//2+1)**2,t//2+1):
                    row_a=[]
                    row_b=[]
                    row_c=[]
                    for beta in range(t//2+1):
                        row_a.append(self.a_shares[inst*(t//2+1)**2+u*(t//2+1)+beta])
                        row_b.append(self.b_shares[inst*(t//2+1)**2+u*(t//2+1)+beta])
                        row_c.append(self.c_shares[inst*(t//2+1)**2+u*(t//2+1)+beta])
                    this_a.append(row_a)
                    this_b.append(row_b)
                    this_c.append(row_c)
                ext_a.aapend(this_a)
                ext_b.aapend(this_b)
                ext_c.aapend(this_c)
            if PARTY_ID!=3:
                self.start_subprotocol(f"wbavss_0",params={"dealer":3,"batching":verification_batching,"externalA":ext_a,"externalB":ext_b,"externalC":ext_c})
        if subprotocol=="wbavss":
            self.return_result([self.a_shares,self.b_shares,self.c_shares])
