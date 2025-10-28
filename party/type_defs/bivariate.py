import galois
from type_defs import UnivariatePolynomial

class BivariatePolynomial:
    def __init__(self, coeffs: list[list[int]], field: type[galois.FieldArray]):
        """
        coeffs: 2D list of integer coefficients, coeffs[i][j] = coefficient of x^i * y^j
        field: Galois field class (e.g., galois.GF(2**8))
        """
        # Sanity checks
        assert all(isinstance(row, list) for row in coeffs), "coeffs must be a 2D list"
        assert len(coeffs) > 0 and len(coeffs[0]) > 0, "coeffs cannot be empty"

        self.field = field
        self.degree_x = len(coeffs) - 1
        self.degree_y = len(coeffs[0]) - 1

        # Convert to field elements
        self.coeffs = [
            [field(c) for c in row]
            for row in coeffs
        ]

    # ---------------- Univariate extraction ----------------
    def univariate_in_x(self, y_value) -> UnivariatePolynomial:
        y_value = self.field(y_value)
        coeffs_x = []
        for i in range(self.degree_x + 1):
            acc = self.field(0)
            for j in range(self.degree_y + 1):
                acc += self.coeffs[i][j] * (y_value ** j)
            coeffs_x.append(int(acc))
        return UnivariatePolynomial(coeffs_x, self.field)

    def univariate_in_y(self, x_value) -> UnivariatePolynomial:
        x_value = self.field(x_value)
        coeffs_y = []
        for j in range(self.degree_y + 1):
            acc = self.field(0)
            for i in range(self.degree_x + 1):
                acc += self.coeffs[i][j] * (x_value ** i)
            coeffs_y.append(int(acc))
        return UnivariatePolynomial(coeffs_y, self.field)

    # ---------------- Evaluation ----------------
    def __call__(self, x, y):
        x = self.field(x)
        y = self.field(y)
        result = self.field(0)
        for i in range(self.degree_x + 1):
            for j in range(self.degree_y + 1):
                result += self.coeffs[i][j] * (x ** i) * (y ** j)
        return result

    def __repr__(self):
        terms = []
        for i, row in enumerate(self.coeffs):
            for j, c in enumerate(row):
                if c != 0:
                    term = str(int(c))
                    if i > 0:
                        term += f"*x^{i}" if i > 1 else "*x"
                    if j > 0:
                        term += f"*y^{j}" if j > 1 else "*y"
                    terms.append(term)
        return " + ".join(terms) if terms else "0"

    # ---------------- Serialization ----------------
    def to_bytes(self) -> bytes:
        """
        Serialize coefficients in row-major order (x-major, then y).
        """
        itemsize = self.field(0).dtype.itemsize
        return b"".join(
            int(self.coeffs[i][j]).to_bytes(itemsize, "little")
            for i in range(self.degree_x + 1)
            for j in range(self.degree_y + 1)
        )

    @classmethod
    def from_bytes(cls, b: bytes, field: type[galois.FieldArray], degree_x: int, degree_y: int):
        """
        Deserialize from bytes (little-endian integer encoding).
        """
        itemsize = field(0).dtype.itemsize
        coeffs = []
        offset = 0
        for i in range(degree_x + 1):
            row = []
            for j in range(degree_y + 1):
                chunk = b[offset:offset + itemsize]
                row.append(int.from_bytes(chunk, "little"))
                offset += itemsize
            coeffs.append(row)
        return cls(coeffs, field)

    @staticmethod
    def get_size(degree_x: int, degree_y: int, field: type[galois.FieldArray]) -> int:
        return (degree_x + 1) * (degree_y + 1) * field(0).dtype.itemsize
