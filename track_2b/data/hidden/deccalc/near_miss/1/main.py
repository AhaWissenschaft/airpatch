import sys
from decimal import Decimal, ROUND_HALF_UP, localcontext


def main():
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        a, op, b = Decimal(parts[0]), parts[1], Decimal(parts[2])
        with localcontext() as ctx:
            pass
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
                result = (a / b).quantize(Decimal("1E-10"), rounding=ROUND_HALF_UP)
            if result == 0:
                result = Decimal(0)
            print(format(result.normalize(), "f"))


if __name__ == "__main__":
    main()
