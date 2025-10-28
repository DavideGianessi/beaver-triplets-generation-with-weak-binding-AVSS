import galois
import numpy as np

class UnivariatePolynomial:
    def __init__(self, coeffs: list[int], field: type[galois.FieldArray]):
        """
        coeffs: array of coefficients, lowest degree first
        field: Galois field
        """
        self.coeffs = [field(c) for c in coeffs]
        self.degree = len(coeffs) - 1
        self.field = field

    def __call__(self, x):
        x = self.field(x)
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

    def to_bytes(self) -> bytes:
        return b"".join(int(c).to_bytes(self.field(0).dtype.itemsize, "little") for c in self.coeffs)

    @classmethod
    def from_bytes(cls, b: bytes, field: type[galois.FieldArray], degree: int):
        itemsize= field(0).dtype.itemsize
        coeffs = [int.from_bytes(b[i*itemsize:(i+1)*itemsize], "little") for i in range(degree + 1)]
        return cls(coeffs, field)

    @staticmethod
    def get_size(degree: int, field : type[galois.FieldArray]) -> int:
        return (degree+1)*field(0).dtype.itemsize
