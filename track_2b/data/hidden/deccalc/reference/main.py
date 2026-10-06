import sys
from fractions import Fraction

PLACES = 10


def divide(a, b):
    q = a / b
    n = int(abs(q) * 10 ** PLACES + Fraction(1, 2))
    result = Fraction(n, 10 ** PLACES)
    return -result if q < 0 else result


def fmt(value):
    """Plain decimal text of a fraction whose denominator divides a power of ten."""
    sign = "-" if value < 0 else ""
    value = abs(value)
    scale = 0
    while value.denominator != 1:
        value *= 10
        scale += 1
    digits = str(value.numerator)
    if not scale:
        return sign + digits
    digits = digits.rjust(scale + 1, "0")
    return sign + digits[:-scale] + "." + digits[-scale:]


def main():
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        a, op, b = Fraction(parts[0]), parts[1], Fraction(parts[2])
        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        elif op == "*":
            result = a * b
        elif b == 0:
            print("ERROR")
            continue
        else:
            result = divide(a, b)
        print(fmt(result))


if __name__ == "__main__":
    main()
