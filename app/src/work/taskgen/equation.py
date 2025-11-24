from random import randint
from typing import List, Tuple, Union
import math


number = Union[float, int]


class Equation:
    def __init__(self, coeffs: List[Tuple[number, int]], roots: List[Union[int, float, complex]], eq_after_coef_n: int):
        self.coeffs = coeffs
        self.roots = roots
        self.eq_after_coef_n = eq_after_coef_n

    def int2pow(num: int) -> str:
        symbols = "⁰¹²³⁴⁵⁶⁷⁸⁹"
        return str(map(lambda x: symbols[int(x)], str(num)))

    def __str__(self):
        out = ""
        for i, c in enumerate(self.coeffs):
            if (i > 0 and i != self.eq_after_coef_n+1) or c[0] < 0:
                out += "+"if c[0] >= 0 else ""
            out += str(c[0])
            if c[1] > -1:
                out += "x"
                if c[1] > 1:
                    out += self.int2pow(c[1])
            if self.eq_after_coef_n == i:
                out += " = "
        out += " | Roots: "
        out += " ".join([str(r) for r in self.roots])
        return out


def randint_nozero(a: int, b: int) -> int:
    x = 0
    while x == 0:
        x = randint(a, b)
    return x


def eq_level1():
    c1 = randint_nozero(-10, 20)
    ans = randint(-30, 50)
    c2 = c1*ans
    return Equation(
        [
            (c1, 1),
            (c2, -1)
        ],
        [
            ans
        ],
        0
    )

def eq_level2():
    r1 = randint_nozero(-30, 50)
    r2 = randint_nozero(-30, 50)
    


if __name__ == '__main__':
    for _ in range(5):
        print(eq_level1())
    for _ in range(5):
        print(eq_level2())