import galois
from type_defs import BivariatePolynomial

class TrivariatePolynomial:
    def __init__(self, coeffs: list[list[list[int]]], field: type[galois.FieldArray]):
        """
        coeffs: 3D list of integer coefficients, coeffs[i][j][k] = coefficient of x^i * y^j * z^k
        field: Galois field class (e.g. galois.GF(2**8))
        """
        # Sanity checks
        assert isinstance(coeffs, list) and all(isinstance(row, list) for row in coeffs), \
            "coeffs must be a 3D list"
        assert len(coeffs) > 0 and len(coeffs[0]) > 0 and len(coeffs[0][0]) > 0, \
            "coeffs cannot be empty"

        self.field = field
        self.degree_x = len(coeffs) - 1
        self.degree_y = len(coeffs[0]) - 1
        self.degree_z = len(coeffs[0][0]) - 1

        # Convert to field elements
        self.coeffs = [
            [
                [field(c) for c in row_z]
                for row_z in row_y
            ]
            for row_y in coeffs
        ]

    # ---------------- Bivariate extraction ----------------
    def bivariate_in_xy(self, z_value) -> BivariatePolynomial:
        z_value = self.field(z_value)
        coeffs_xy = []
        for i in range(self.degree_x + 1):
            row_xy = []
            for j in range(self.degree_y + 1):
                acc = self.field(0)
                for k in range(self.degree_z + 1):
                    acc += self.coeffs[i][j][k] * (z_value ** k)
                row_xy.append(int(acc))
            coeffs_xy.append(row_xy)
        return BivariatePolynomial(coeffs_xy, self.field)

    def bivariate_in_xz(self, y_value) -> BivariatePolynomial:
        y_value = self.field(y_value)
        coeffs_xz = []
        for i in range(self.degree_x + 1):
            row_xz = []
            for k in range(self.degree_z + 1):
                acc = self.field(0)
                for j in range(self.degree_y + 1):
                    acc += self.coeffs[i][j][k] * (y_value ** j)
                row_xz.append(int(acc))
            coeffs_xz.append(row_xz)
        return BivariatePolynomial(coeffs_xz, self.field)

    def bivariate_in_yz(self, x_value) -> BivariatePolynomial:
        x_value = self.field(x_value)
        coeffs_yz = []
        for j in range(self.degree_y + 1):
            row_yz = []
            for k in range(self.degree_z + 1):
                acc = self.field(0)
                for i in range(self.degree_x + 1):
                    acc += self.coeffs[i][j][k] * (x_value ** i)
                row_yz.append(int(acc))
            coeffs_yz.append(row_yz)
        return BivariatePolynomial(coeffs_yz, self.field)

    # ---------------- Evaluation ----------------
    def __call__(self, x, y, z):
        x = self.field(x)
        y = self.field(y)
        z = self.field(z)
        result = self.field(0)
        for i in range(self.degree_x + 1):
            for j in range(self.degree_y + 1):
                for k in range(self.degree_z + 1):
                    result += self.coeffs[i][j][k] * (x ** i) * (y ** j) * (z ** k)
        return result

    def __repr__(self):
        terms = []
        for i, row_y in enumerate(self.coeffs):
            for j, row_z in enumerate(row_y):
                for k, c in enumerate(row_z):
                    if c != 0:
                        term = str(int(c))
                        if i > 0:
                            term += f"*x^{i}" if i > 1 else "*x"
                        if j > 0:
                            term += f"*y^{j}" if j > 1 else "*y"
                        if k > 0:
                            term += f"*z^{k}" if k > 1 else "*z"
                        terms.append(term)
        return " + ".join(terms) if terms else "0"

    # ---------------- Serialization ----------------
    def to_bytes(self) -> bytes:
        """
        Serialize coefficients in row-major order (x-major, then y, then z).
        """
        itemsize = self.field(0).dtype.itemsize
        return b"".join(
            int(self.coeffs[i][j][k]).to_bytes(itemsize, "little")
            for i in range(self.degree_x + 1)
            for j in range(self.degree_y + 1)
            for k in range(self.degree_z + 1)
        )

    @classmethod
    def from_bytes(cls, b: bytes, field: type[galois.FieldArray],
                   degree_x: int, degree_y: int, degree_z: int):
        """
        Deserialize from bytes (little-endian integer encoding).
        """
        itemsize = field(0).dtype.itemsize
        coeffs = []
        offset = 0
        for i in range(degree_x + 1):
            row_y = []
            for j in range(degree_y + 1):
                row_z = []
                for k in range(degree_z + 1):
                    chunk = b[offset:offset + itemsize]
                    row_z.append(int.from_bytes(chunk, "little"))
                    offset += itemsize
                row_y.append(row_z)
            coeffs.append(row_y)
        return cls(coeffs, field)

    @staticmethod
    def get_size(degree_x: int, degree_y: int, degree_z: int, field: type[galois.FieldArray]) -> int:
        return (degree_x + 1) * (degree_y + 1) * (degree_z + 1) * field(0).dtype.itemsize
