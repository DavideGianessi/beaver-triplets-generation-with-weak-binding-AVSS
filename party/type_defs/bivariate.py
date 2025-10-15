import galois
import numpy as np
from univariate import UnivariatePolynomial

class BivariatePolynomial:
    def __init__(self, coeffs: np.ndarray, field: galois.FieldArray):
        """
        coeffs: 2D array of coefficients, coeffs[i,j] corresponds to x^i * y^j
        field: Galois field
        """
        assert coeffs.ndim == 2, "Coefficients must be a 2D array"
        self.coeffs = field(coeffs)
        self.field = field
        self.degree_x = coeffs.shape[0] - 1
        self.degree_y = coeffs.shape[1] - 1

    # ---------------- Univariate extraction ----------------
    def univariate_in_x(self, y_value) -> UnivariatePolynomial:
        y_value = self.field(y_value)
        coeffs_x = np.sum(self.coeffs * y_value**np.arange(self.coeffs.shape[1]), axis=1)
        return UnivariatePolynomial(coeffs_x, self.field)

    def univariate_in_y(self, x_value) -> UnivariatePolynomial:
        x_value = self.field(x_value)
        coeffs_y = np.sum(self.coeffs * x_value**np.arange(self.coeffs.shape[0])[:, None], axis=0)
        return UnivariatePolynomial(coeffs_y, self.field)

    # ---------------- Evaluation ----------------
    def __call__(self, x, y):
        x = self.field(x)
        y = self.field(y)
        result = self.field(0)
        for i in range(self.coeffs.shape[0]):
            for j in range(self.coeffs.shape[1]):
                result += self.coeffs[i,j] * x**i * y**j
        return result

    def __repr__(self):
        return f"BivariatePolynomial(coeffs shape={self.coeffs.shape}) over {self.field}"

    # ---------------- Serialization ----------------
    def to_bytes(self) -> bytes:
        """Serialize the coefficients into bytes by flattening row-major"""
        return self.coeffs.flatten().tobytes()

    @classmethod
    def from_bytes(cls, b: bytes, field: galois.FieldArray, degree_x: int, degree_y: int):
        """Deserialize bytes into a BivariatePolynomial given degrees and field"""
        coeffs = np.frombuffer(b, dtype=field.dtype, count=(degree_x+1)*(degree_y+1))
        coeffs = coeffs.reshape((degree_x+1, degree_y+1))
        return cls(coeffs, field)
