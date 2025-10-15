import galois
import numpy as np
from bivariate import BivariatePolynomial

class TrivariatePolynomial:
    def __init__(self, coeffs: np.ndarray, field: galois.FieldArray):
        assert coeffs.ndim == 3, "Coefficients must be a 3D array"
        self.coeffs = field(coeffs)
        self.field = field
        self.degree_x = coeffs.shape[0] - 1
        self.degree_y = coeffs.shape[1] - 1
        self.degree_z = coeffs.shape[2] - 1

    # ---------------- Bivariate extraction ----------------
    def bivariate_in_xy(self, z_value) -> BivariatePolynomial:
        z_value = self.field(z_value)
        powers = z_value ** np.arange(self.coeffs.shape[2])  # z^k
        coeffs_xy = np.tensordot(self.coeffs, powers, axes=(2, 0))  # sum over k
        return BivariatePolynomial(coeffs_xy, self.field)

    def bivariate_in_xz(self, y_value) -> BivariatePolynomial:
        y_value = self.field(y_value)
        powers = y_value ** np.arange(self.coeffs.shape[1])  # y^j
        coeffs_xz = np.tensordot(self.coeffs, powers, axes=(1, 0))  # sum over j
        return BivariatePolynomial(coeffs_xz, self.field)

    def bivariate_in_yz(self, x_value) -> BivariatePolynomial:
        x_value = self.field(x_value)
        powers = x_value ** np.arange(self.coeffs.shape[0])  # x^i
        coeffs_yz = np.tensordot(self.coeffs, powers, axes=(0, 0))  # sum over i
        return BivariatePolynomial(coeffs_yz, self.field)

    # ---------------- Evaluation ----------------
    def __call__(self, x, y, z):
        x = self.field(x)
        y = self.field(y)
        z = self.field(z)
        result = self.field(0)
        for i in range(self.coeffs.shape[0]):
            for j in range(self.coeffs.shape[1]):
                for k in range(self.coeffs.shape[2]):
                    result += self.coeffs[i,j,k] * x**i * y**j * z**k
        return result

    def __repr__(self):
        return f"TrivariatePolynomial(coeffs shape={self.coeffs.shape}) over {self.field}"

    def to_bytes(self) -> bytes:
        return self.coeffs.flatten().tobytes()

    @classmethod
    def from_bytes(cls, b: bytes, field: galois.FieldArray,
                   degree_x: int, degree_y: int, degree_z: int):
        coeffs = np.frombuffer(b, dtype=field.dtype,
                               count=(degree_x+1)*(degree_y+1)*(degree_z+1))
        coeffs = coeffs.reshape((degree_x+1, degree_y+1, degree_z+1))
        return cls(coeffs, field)
