from type_defs import TrivariatePolynomial,BivariatePolynomial,UnivariatePolynomial
from config import PARTY_ID,N,t,p

def external_validity(a,b,c,T,i,GF):
    for beta in range(t//2):
        for gamma in range(t//2):
            if T(beta,gamma) != a[beta][gamma]*b[beta][gamma]-c[beta][gamma]:
                return False
    return True
