import galois
import numpy as np
from type_defs import UnivariatePolynomial

def construct_polynomial(points, n, t, GF):
    num_Q = n + t + 1
    num_E = t + 1
    num_vars = num_Q + num_E
    N=len(points)
    if N <= n + t:
        return None

    A_rows = []
    for x, y in points:
        Q_coeffs = [x**i for i in range(num_Q)]
        E_coeffs = [-y * (x**i) for i in range(num_E)]
        row = GF(Q_coeffs + E_coeffs)
        if len(A_rows) == 0:
            A_rows.append(row)
        else:
            temp = GF(A_rows + [row])
            if np.linalg.matrix_rank(temp) > np.linalg.matrix_rank(GF(A_rows)):
                A_rows.append(row)
    
    m = len(A_rows)
    if m > num_vars:
        return None
    
    while len(A_rows) < num_vars:
        A_rows.append(GF.Zeros(num_vars))
    
    A = GF(A_rows)

    kernel = A.null_space()
    dim = kernel.shape[0]
    if dim == 0:
        return None
    
    valid_Ps = []

    for i in range(kernel.shape[0]):
        vec = kernel[i, :]
        Q_vec = galois.Poly(vec[:num_Q], field=GF)
        E_vec = galois.Poly(vec[num_Q:], field=GF)
        P_vec, rem = divmod(Q_vec, E_vec)
        if rem == 0:
            valid_Ps.append(P_vec)

    if len(valid_Ps) == 0:
        return None

    first_P = valid_Ps[0]
    for P in valid_Ps[1:]:
        if P != first_P:
            return None

    coeffs=list(first_P.coeffs)+[GF(0) for i in range(n+1-len(first_P.coeffs))]
    P=UnivariatePolynomial(coeffs,GF)
    thesum=sum(P(x) == y for x, y in points)
    if sum(P(x) == y for x, y in points) >= N - t:
        return P
    return None
