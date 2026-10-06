import sys


def main():
    nets = {}
    vats = {}
    for line in sys.stdin:
        if not line.strip() or line.startswith("#"):
            continue
        desc, qty, price, rate = line.split(";")
        rate = rate.strip()
        amount = float(qty) * float(price)
        nets[rate] = nets.get(rate, 0) + amount
        vats[rate] = vats.get(rate, 0) + round(amount * float(rate) / 100, 2)
    total = 0
    for rate in sorted(nets):
        total += nets[rate] + vats[rate]
        print(f"{rate}% net {nets[rate]:.2f} vat {vats[rate]:.2f}")
    print(f"total {total:.2f}")
    print(f"payable {round(total * 20) / 20:.2f}")


if __name__ == "__main__":
    main()
