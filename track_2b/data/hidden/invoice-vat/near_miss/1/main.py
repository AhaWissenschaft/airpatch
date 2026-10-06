import sys
from decimal import Decimal, ROUND_HALF_UP

CENT = Decimal("0.01")
STEP = Decimal("0.05")


def cents(value):
    return value.quantize(CENT, rounding=ROUND_HALF_UP)


def fmt(value):
    value = cents(value)
    return str(abs(value) if value == 0 else value)


def main():
    nets, vats = {}, {}
    for raw in sys.stdin:
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        _, qty, price, rate = (field.strip() for field in line.split(";"))
        rate = Decimal(rate).quantize(Decimal("0.1"))
        amount = cents(Decimal(qty) * Decimal(price))
        nets[rate] = nets.get(rate, Decimal("0")) + amount
        vats[rate] = vats.get(rate, Decimal("0")) + cents(amount * rate / 100)
    total = Decimal("0")
    for rate in sorted(nets):
        vat = vats[rate]
        total += nets[rate] + vat
        print(f"{rate}% net {fmt(nets[rate])} vat {fmt(vat)}")
    payable = (total / STEP).quantize(Decimal("1"), rounding=ROUND_HALF_UP) * STEP
    print("total", fmt(total))
    print("payable", fmt(payable))


if __name__ == "__main__":
    main()
