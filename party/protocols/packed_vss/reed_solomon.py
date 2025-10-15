import galois
import numpy as np

def reconstruct_polynomial(points, t, GF):
    """
    Reconstruct a degree ≤ t polynomial P(x) from possibly corrupted points (x_i, y_i)
    over a finite field GF.
    
    Args:
        points: list of tuples (x_i, y_i) where x_i, y_i are elements of GF
        t: maximum number of errors to tolerate
        GF: a galois.Field class, e.g., GF = galois.GF(2**8)
    
    Returns:
        univariatePolynomial P if unique and consistent, else None
    """
    n = len(points)
    if n < 2 * t + 1:
        # Guaranteed non-uniqueness
        return None

    num_q = 2 * t + 1
    num_e = t               # e_t = 1 fixed
    num_unknowns = num_q + num_e

    # Build linear system over GF
    A = GF.Zeros((n, num_unknowns))
    b = GF.Zeros(n)

    for i, (x, y) in enumerate(points):
        # Q(x) part: x^0 ... x^(2t)
        for j in range(num_q):
            A[i, j] = x**j
        # E(x) part: -y * x^k for k = 0..t-1
        for k in range(num_e):
            A[i, num_q + k] = -y * (x**k)
        # RHS: y * x^t
        b[i] = y * (x**t)

    # Solve the linear system over GF
    try:
        coeffs = galois.linalg.solve(A, b)
    except galois.linalg.LinAlgError:
        return None  # No solution or inconsistent

    # Extract Q and E coefficients
    q_coeffs = [int(coeffs[i]) for i in range(num_q)]
    e_coeffs = [int(coeffs[num_q + i]) for i in range(num_e)] + [1]  # append e_t=1

    # Construct polynomials using galois.Poly
    Q = galois.Poly(q_coeffs, field=GF)
    E = galois.Poly(e_coeffs, field=GF)

    # Divide Q by E
    P, remainder = divmod(Q, E)
    if remainder != 0:
        return None

    # Optional verification: check at least 2t+1 points match
    match_count = sum(1 for x, y in points if P(x) == y)
    if match_count < 2 * t + 1:
        return None

    return P
