import sys
from decimal import Decimal


def main():
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        a, op, b = Decimal(parts[0]), parts[1], Decimal(parts[2])
        if op == "+":
            result = a + b
        elif op == "-":
            result = a - b
        elif op == "*":
            result = a * b
        else:
            result = round(a / b, 10)
        print(result)


if __name__ == "__main__":
    main()
