from type_defs import TrivariatePolynomial,BivariatePolynomial,UnivariatePolynomial
from config import PARTY_ID,N,t,p
from util.logging import log

def external_validity(a,b,c,T,i,GF):
    #log("checking_validity -------------")
    #log(f"{a=}")
    #log(f"{b=}")
    #log(f"{c=}")
    #log(f"{T=}")
    #log(f"{i=}")
    for beta in range(t//2+1):
        for gamma in range(t//2+1):
            #log(f"{T(-beta,-gamma)=}")
            #log(f"{a[gamma][beta]*b[gamma][beta]-c[gamma][beta]=}\n")
            if T(-beta,-gamma) != a[gamma][beta]*b[gamma][beta]-c[gamma][beta]:
                return False
    return True
