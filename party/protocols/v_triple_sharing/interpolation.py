import galois
from type_defs import BivariatePolynomial, TrivariatePolynomial, UnivariatePolynomial

def lagrange_interpolate_univariate(points: list[tuple[int, int]], field: type[galois.FieldArray]) -> UnivariatePolynomial:
    n = len(points)
    assert n > 0, "Need at least one point"
    xs, ys = zip(*points)
    xs = list(xs)
    ys = list(ys)
    if len(set(xs)) != n:
        raise ValueError("All x_i values must be distinct")
    zero_poly = UnivariatePolynomial([0], field)
    x_poly = UnivariatePolynomial([0, 1], field)
    P = zero_poly
    for i in range(n):
        xi = field(xs[i])
        yi = field(ys[i])
        Li = UnivariatePolynomial([1], field)
        denom = field(1)
        for j in range(n):
            if i == j:
                continue
            xj = field(xs[j])
            Li *= (x_poly + UnivariatePolynomial([-int(xj)], field))
            denom *= (xi - xj)
        scale = yi / denom
        term = Li * UnivariatePolynomial([int(scale)], field)
        P += term
    return P

def lagrange_interpolate_bivariate(points: list[tuple[int, UnivariatePolynomial]],
                                   field: type[galois.FieldArray]) -> BivariatePolynomial:
    n = len(points)
    assert n > 0, "Need at least one (x, UnivariatePolynomial) pair"
    xs, polys_y = zip(*points)
    if len(set(xs)) != n:
        raise ValueError("All x_i must be distinct")
    field = polys_y[0].field
    deg_y = polys_y[0].degree
    for p in polys_y:
        if p.field is not field:
            raise ValueError("All univariates must be over the same field")
        if p.degree != deg_y:
            raise ValueError("All univariates must have the same y-degree")
    x_poly = UnivariatePolynomial([0, 1], field)
    zero_bivar = BivariatePolynomial([[0] * (deg_y + 1)], field)
    A = zero_bivar
    for i in range(n):
        xi = field(xs[i])
        Pi_y = polys_y[i]
        Li = UnivariatePolynomial([1], field)
        denom = field(1)
        for j in range(n):
            if i == j:
                continue
            xj = field(xs[j])
            Li *= (x_poly + UnivariatePolynomial([-int(xj)], field))
            denom *= (xi - xj)
        Li_scaled = Li * UnivariatePolynomial([int(field(1) / denom)], field)
        term_coeffs = [
            [int(cy * cx) for cy in Pi_y.coeffs]
            for cx in Li_scaled.coeffs
        ]
        term = BivariatePolynomial(term_coeffs, field)
        A += term
    return A

def lagrange_interpolate_trivariate(points: list[tuple[int, BivariatePolynomial]],
                                    field: type[galois.FieldArray]) -> TrivariatePolynomial:
    n = len(points)
    assert n > 0, "Need at least one (z, BivariatePolynomial) pair"
    zs, bivariates = zip(*points)
    if len(set(zs)) != n:
        raise ValueError("All z_i must be distinct")
    field = bivariates[0].field
    deg_x = bivariates[0].degree_x
    deg_y = bivariates[0].degree_y
    for b in bivariates:
        if b.field is not field:
            raise ValueError("All bivariates must be over the same field")
        if b.degree_x != deg_x or b.degree_y != deg_y:
            raise ValueError("All bivariates must have the same x and y degrees")
    z_poly = UnivariatePolynomial([0, 1], field)
    zero_trivar = TrivariatePolynomial([[[0] * (deg_y + 1)] * (deg_x + 1)], field)
    T = zero_trivar
    for i in range(n):
        zi = field(zs[i])
        Bi_xy = bivariates[i]
        Li = UnivariatePolynomial([1], field)
        denom = field(1)
        for j in range(n):
            if i == j:
                continue
            zj = field(zs[j])
            Li *= (z_poly + UnivariatePolynomial([-int(zj)], field))
            denom *= (zi - zj)

        Li_scaled = Li * UnivariatePolynomial([int(field(1) / denom)], field)
        term_coeffs = [
            [
                [int(cxy * cz) for cxy in row]
                for row in Bi_xy.coeffs
            ]
            for cz in Li_scaled.coeffs
        ]
        term = TrivariatePolynomial(term_coeffs, field)
        T += term
    return T

def interpolate_trivariate_from_grid(values_3d: list[list[list[int]]],
                                     field: type[galois.FieldArray]) -> TrivariatePolynomial:
    n = len(values_3d) - 1
    assert n >= 0
    assert all(len(values_3d[x]) == n + 1 for x in range(n + 1))
    assert all(len(values_3d[x][y]) == n + 1 for x in range(n + 1) for y in range(n + 1))
    univariates_grid = [
        [
            lagrange_interpolate_univariate(
                [( -z, values_3d[x][y][z] ) for z in range(n + 1)], field
            )
            for y in range(n + 1)
        ]
        for x in range(n + 1)
    ]
    bivariates = [
        lagrange_interpolate_bivariate(
            [( -y, univariates_grid[x][y] ) for y in range(n + 1)],
            field
        )
        for x in range(n + 1)
    ]
    trivariate = lagrange_interpolate_trivariate(
        [( -x, bivariates[x] ) for x in range(n + 1)],
        field
    )
    return trivariate
