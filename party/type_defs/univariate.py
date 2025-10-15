import galois
import numpy as np

class UnivariatePolynomial:
    def __init__(self, coeffs: np.ndarray, field: galois.FieldArray):
        """
        coeffs: array of coefficients, lowest degree first
        field: Galois field
        """
        self.coeffs = field(coeffs)
        self.degree = len(coeffs) - 1
        self.field = field

    def __call__(self, x):
        x = self.field(x)
        result = self.field(0)
        for i, c in enumerate(self.coeffs):
            result += c * x**i
        return result

    def __repr__(self):
        return f"UnivariatePolynomial({self.coeffs}) over {self.field}"

    def to_bytes(self) -> bytes:
        return self.coeffs.tobytes()

    @classmethod
    def from_bytes(cls, b: bytes, field: galois.FieldArray, degree: int):
        coeffs = np.frombuffer(b, dtype=field.dtype, count=degree+1)
        return cls(coeffs, field)
