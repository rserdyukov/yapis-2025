# Runtime.py
import math
import ast


# ==========================================
# RUNTIME TYPES & HELPERS
# ==========================================

class Ref:
    """Обертка для ссылок, т.к. в байт-коде python нет передачи по ссылке для чисел."""

    def __init__(self, value): self.value = value

    def __repr__(self): return f"{self.value}"

    def __getattr__(self, item):
        if item == 'value': return super().__getattribute__(item)
        return getattr(self.value, item)

    def _val(self, other): return other.value if isinstance(other, Ref) else other

    # Арифметика
    def __add__(self, other): return self.value + self._val(other)

    def __radd__(self, other): return self._val(other) + self.value

    def __sub__(self, other): return self.value - self._val(other)

    def __rsub__(self, other): return self._val(other) - self.value

    def __mul__(self, other): return self.value * self._val(other)

    def __rmul__(self, other): return self._val(other) * self.value

    def __truediv__(self, other): return self.value / self._val(other)

    def __rtruediv__(self, other): return self._val(other) / self.value

    def __mod__(self, other): return self.value % self._val(other)

    def __len__(self): return len(self.value)

    def __getitem__(self, item): return self.value[item]

    def __setitem__(self, key, value): self.value[key] = value

    def __iter__(self): return iter(self.value)

    def __eq__(self, other): return self.value == self._val(other)

    def __lt__(self, other): return self.value < self._val(other)

    def __bool__(self): return bool(self.value)

    def __int__(self): return int(self.value)

    def __float__(self): return float(self.value)

    def __index__(self): return int(self.value)


class Vector:
    """класс для реализации операции над векторами"""
    def __init__(self, values):
        if isinstance(values, (list, tuple)):
            if values and isinstance(values[0], list):
                self.values = [item for sublist in values for item in sublist]
            else:
                self.values = list(values)
        elif isinstance(values, Vector):
            self.values = list(values.values)
        else:
            self.values = [values]

        self.n_cols = len(self.values)

    def __len__(self):
        return len(self.values)

    def __repr__(self):
        return f"({', '.join(map(str, self.values))})"

    def _val(self, other):
        return other.value if isinstance(other, Ref) else other

    def __add__(self, other):
        other = self._val(other)
        if isinstance(other, (list, tuple)): other = Vector(other)
        if isinstance(other, Vector):
            if len(self) != len(other): raise ValueError("Vector length mismatch")
            return Vector([a + b for a, b in zip(self.values, other.values)])
        if isinstance(other, Matrix):
            flat = [x for row in other.rows for x in row]
            limit = min(len(self.values), len(flat))
            return Vector([self.values[i] + flat[i] for i in range(limit)])
        if isinstance(other, (int, float)): return Vector([x + other for x in self.values])
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        other = self._val(other)
        if isinstance(other, Vector): return Vector([a - b for a, b in zip(self.values, other.values)])
        if isinstance(other, Matrix):
            flat = [x for row in other.rows for x in row]
            limit = min(len(self.values), len(flat))
            return Vector([self.values[i] - flat[i] for i in range(limit)])
        if isinstance(other, (int, float)): return Vector([x - other for x in self.values])
        return NotImplemented

    def __rsub__(self, other):
        other = self._val(other)
        if isinstance(other, (int, float)): return Vector([other - x for x in self.values])
        return NotImplemented

    def __mul__(self, other):
        other = self._val(other)
        if isinstance(other, (int, float)): return Vector([x * other for x in self.values])
        if isinstance(other, (Vector, list, tuple)):
            if isinstance(other, (list, tuple)): other = Vector(other)
            if len(self) != len(other): raise ValueError("Mismatch")
            return sum(a * b for a, b in zip(self.values, other.values))
        if isinstance(other, Matrix):
            if len(self) != other.n_rows: raise ValueError("Mismatch V*M")
            return Vector(
                [sum(self.values[r] * other.rows[r][c] for r in range(other.n_rows)) for c in range(other.n_cols)])
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        other = self._val(other)
        if isinstance(other, (int, float)): return Vector([x / other for x in self.values])
        return NotImplemented

    def __getitem__(self, item):
        return self.values[item]

    def norm(self):
        return math.sqrt(sum(x ** 2 for x in self.values))


class Matrix:
    """класс для реализации операции над матрицами"""
    def __init__(self, rows):
        if isinstance(rows, list):
            if not rows:
                self.rows = []
            elif not isinstance(rows[0], list):
                self.rows = [rows]
            else:
                self.rows = rows
        else:
            self.rows = []
        self.n_rows = len(self.rows)
        self.n_cols = len(self.rows[0]) if self.n_rows > 0 else 0

    def __len__(self):
        if self.n_rows == 1: return self.n_cols
        return self.n_rows

    def __repr__(self):
        return f"[{', '.join(map(str, self.rows))}]"

    def _val(self, other):
        return other.value if isinstance(other, Ref) else other

    @classmethod
    def from_args(cls, value=0, columns=1, rows=1):
        if isinstance(value, Ref): value = value.value
        if isinstance(columns, Ref): columns = columns.value
        if isinstance(rows, Ref): rows = rows.value
        try:
            columns = int(columns)
            rows = int(rows)
        except:
            pass
        return cls([[value] * columns for _ in range(rows)])

    def __add__(self, other):
        other = self._val(other)
        if isinstance(other, Vector): other = Matrix([other.values])
        if isinstance(other, list):
            if self.n_rows == 1 and self.n_cols == len(other):
                other = Matrix([other])
            else:
                other = Matrix(other)

        if isinstance(other, Matrix):
            if other.n_rows == 1 and other.n_cols == 1: return self + other.rows[0][0]
            if self.n_rows == 1 and self.n_cols == 1: return other + self.rows[0][0]
            if self.n_rows != other.n_rows or self.n_cols != other.n_cols: raise ValueError("Matrix dimension mismatch")
            return Matrix(
                [[self.rows[r][c] + other.rows[r][c] for c in range(self.n_cols)] for r in range(self.n_rows)])

        if isinstance(other, (int, float)):
            return Matrix([[self.rows[r][c] + other for c in range(self.n_cols)] for r in range(self.n_rows)])
        return NotImplemented

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        other = self._val(other)
        if isinstance(other, Vector): other = Matrix([other.values])
        if isinstance(other, list):
            if self.n_rows == 1 and self.n_cols == len(other):
                other = Matrix([other])
            else:
                other = Matrix(other)

        if isinstance(other, Matrix):
            if other.n_rows == 1 and other.n_cols == 1: return self - other.rows[0][0]
            if self.n_rows == 1 and self.n_cols == 1:
                val = self.rows[0][0]
                return Matrix([[val - other.rows[r][c] for c in range(other.n_cols)] for r in range(other.n_rows)])
            if self.n_rows != other.n_rows or self.n_cols != other.n_cols: raise ValueError("Matrix dimension mismatch")
            return Matrix(
                [[self.rows[r][c] - other.rows[r][c] for c in range(self.n_cols)] for r in range(self.n_rows)])

        if isinstance(other, (int, float)):
            return Matrix([[self.rows[r][c] - other for c in range(self.n_cols)] for r in range(self.n_rows)])
        return NotImplemented

    def __rsub__(self, other):
        other = self._val(other)
        if isinstance(other, Vector): other = Matrix([other.values])
        if isinstance(other, list): other = Matrix(other)
        if isinstance(other, (int, float)):
            return Matrix([[other - self.rows[r][c] for c in range(self.n_cols)] for r in range(self.n_rows)])
        return NotImplemented

    def __mul__(self, other):
        other = self._val(other)
        # 1. Matrix * Vector -> Vector
        if isinstance(other, Vector):
            if self.n_cols != len(other): raise ValueError(f"Mismatch M*V: cols {self.n_cols} != len {len(other)}")
            return Vector(
                [sum(self.rows[r][c] * other.values[c] for c in range(self.n_cols)) for r in range(self.n_rows)])

        # 2. Matrix * Matrix -> Matrix
        if isinstance(other, Matrix):
            if self.n_cols == other.n_rows:
                return Matrix([[sum(a * b for a, b in zip(row, col)) for col in zip(*other.rows)] for row in self.rows])
            # Снисходительность: (MxN) * (1xN) -> трактуем как вектор
            if other.n_rows == 1 and self.n_cols == other.n_cols:
                vec_other = Vector(other.rows[0])
                return self * vec_other
            raise ValueError(f"Matrix mul mismatch: ({self.n_rows}x{self.n_cols}) * ({other.n_rows}x{other.n_cols})")

        if isinstance(other, (int, float)): return Matrix([[x * other for x in row] for row in self.rows])
        return NotImplemented

    def __rmul__(self, other):
        return self.__mul__(other)

    def __getitem__(self, item):
        return Vector(self.rows[item])

    def norm(self):
        return math.sqrt(sum(x ** 2 for row in self.rows for x in row))


def vec_norm(obj):
    real_obj = obj.value if isinstance(obj, Ref) else obj
    if hasattr(real_obj, 'norm'): return real_obj.norm()
    if isinstance(real_obj, (int, float)): return abs(real_obj)
    if isinstance(real_obj, list): return math.sqrt(sum(x ** 2 for x in real_obj))
    return 0


def vector_ctor(*args):
    if len(args) == 1:
        val = args[0]
        val = val.value if isinstance(val, Ref) else val
        if isinstance(val, list): return Vector(val)
        if isinstance(val, Vector): return Vector(val.values)
        if isinstance(val, Matrix): return Vector([x for row in val.rows for x in row])
        if isinstance(val, (int, float)): return Vector([val])
    return Vector(list(args))


def matrix_factory(*args, **kwargs):
    if len(args) == 1 and not kwargs:
        val = args[0]
        val = val.value if isinstance(val, Ref) else val
        if isinstance(val, list): return Matrix(val)
        if isinstance(val, Matrix): return Matrix(val.rows)
        if isinstance(val, Vector): return Matrix([val.values])
        if isinstance(val, (int, float)): return Matrix([[val]])
    return Matrix.from_args(*args, **kwargs)


# Глобальные встроенные имена, которые компилятор должен знать
BUILTINS = {'print', 'read', 'write', 'vector', 'matrix', 'len', 'Ref', '_rt_norm', 'Expectation', 'range'}


def get_env():
    def smart_read():
        text = input()
        try:
            val = ast.literal_eval(text)
            if isinstance(val, (list, tuple)): return Vector(val)
            return val
        except (ValueError, SyntaxError):
            return text

    return {
        'print': print, 'read': smart_read, 'write': print,
        'vector': vector_ctor, 'matrix': matrix_factory, 'len': len,
        '_rt_norm': vec_norm, 'Ref': Ref,
        'Expectation': Exception("Expectation Failed"),
        '__name__': '__main__',
        'range': range
    }