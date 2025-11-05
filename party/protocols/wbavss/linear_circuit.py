from type_defs import TrivariatePolynomial,BivariatePolynomial,UnivariatePolynomial
from config import PARTY_ID,N,t,p

def linear_to_bivariate(i,Ss,GF):
    res=BivariatePolynomial([[0]],GF)
    for r in range(4):
        for k in range(1,t//2+1):
            res+=pow(i,r*(t//2)+k,p) * Ss[r]._bivariate_in_y(-k)
    return res



def linear_to_univariate(i,Q):
    res=UnivariatePolynomial([0],GF)
    for k in range(1,t//2+1):
        res+=pow(i,k,p) * Q.univariate_in_y(-k)
    return res
