import sys
from decimal import Decimal


def main():
    totals = {}
    for raw in sys.stdin:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        name, amount = line.split(",", 1)
        name = name.strip()
        totals[name] = totals.get(name, Decimal("0")) + Decimal(amount.strip())
    for name in sorted(totals):
        print(f"{name} {totals[name].quantize(Decimal('0.01'))}")


if __name__ == "__main__":
    main()
