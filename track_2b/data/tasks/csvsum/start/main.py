import sys


def main():
    totals = {}
    for line in sys.stdin:
        name, amount = line.split(",")
        totals[name] = totals.get(name, 0) + float(amount)
    for name, total in totals.items():
        print(name, total)


if __name__ == "__main__":
    main()
