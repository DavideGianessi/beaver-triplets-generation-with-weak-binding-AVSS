import galois

class UnivariatePolynomial:
    def __init__(self, coeffs: list[int], field: type[galois.FieldArray]):
        """
        coeffs: array of coefficients, lowest degree first
        field: Galois field
        """
        self.field = field
        self.coeffs = [field(c%self.field.characteristic) if isinstance(c,int) else c for c in coeffs]
        self.degree = len(coeffs) - 1

    def __call__(self, x):
        if isinstance(x,int):
            x = self.field(x%self.field.characteristic)
        result = self.field(0)
        for i, c in enumerate(self.coeffs):
            result += c * x**i
        return result

    def __repr__(self):
        terms = []
        for i, c in enumerate(self.coeffs):
            if c != 0:
                if i == 0:
                    terms.append(f"{int(c)}")
                elif i == 1:
                    terms.append(f"{int(c)}*x")
                else:
                    terms.append(f"{int(c)}*x^{i}")
        return " + ".join(terms) if terms else "0"

    def __add__(self, other):
        if not isinstance(other, UnivariatePolynomial):
            return NotImplemented
        if self.field is not other.field:
            raise TypeError("Cannot add polynomials over different fields")
        max_len = max(len(self.coeffs), len(other.coeffs))
        coeffs1 = self.coeffs + [self.field(0)] * (max_len - len(self.coeffs))
        coeffs2 = other.coeffs + [self.field(0)] * (max_len - len(other.coeffs))
        new_coeffs = [a + b for a, b in zip(coeffs1, coeffs2)]
        return UnivariatePolynomial(new_coeffs, self.field)

    def __mul__(self, other):
        if isinstance(other, (int, self.field)):
            if isinstance(other,int):
                other=self.field(other%self.field.characteristic)
            new_coeffs = [c * other for c in self.coeffs]
            return UnivariatePolynomial(new_coeffs, self.field)
        if isinstance(other, UnivariatePolynomial):
            if self.field is not other.field:
                raise TypeError("Polynomials must be over the same field")
            deg = self.degree + other.degree
            coeffs = [self.field(0) for _ in range(deg+1)]
            for i, a in enumerate(self.coeffs):
                for j, b in enumerate(other.coeffs):
                    coeffs[i + j] += a * b
            return UnivariatePolynomial(coeffs, self.field)
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __eq__(self, other):
        if not isinstance(other, UnivariatePolynomial):
            return False
        if self.field is not other.field:
            return False
        if self.degree != other.degree:
            return False
        return all(a == b for a, b in zip(self.coeffs, other.coeffs))

    def __neg__(self):
        neg_coeffs = [ -c for c in self.coeffs ]
        return UnivariatePolynomial(neg_coeffs, self.field)

    def __sub__(self, other):
        if not isinstance(other, UnivariatePolynomial):
            return NotImplemented
        if self.field is not other.field:
            raise TypeError("Cannot subtract polynomials over different fields")
        max_len = max(len(self.coeffs), len(other.coeffs))
        coeffs1 = self.coeffs + [self.field(0)] * (max_len - len(self.coeffs))
        coeffs2 = other.coeffs + [self.field(0)] * (max_len - len(other.coeffs))
        new_coeffs = [a - b for a, b in zip(coeffs1, coeffs2)]
        return UnivariatePolynomial(new_coeffs, self.field)

    def to_bytes(self) -> bytes:
        n_bytes = (self.field.characteristic.bit_length() + 7) // 8
        return b"".join(int(c).to_bytes(n_bytes, "little") for c in self.coeffs)

    @classmethod
    def from_bytes(cls, b: bytes, field: type[galois.FieldArray], degree: int):
        itemsize= (field.characteristic.bit_length() + 7) // 8
        coeffs = [int.from_bytes(b[i*itemsize:(i+1)*itemsize], "little") for i in range(degree + 1)]
        return cls(coeffs, field)

    @staticmethod
    def get_size(degree: int, field : type[galois.FieldArray]) -> int:
        n_bytes = (field.characteristic.bit_length() + 7) // 8
        return (degree+1)*n_bytes
