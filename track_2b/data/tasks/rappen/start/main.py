import math
import sys


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        amount = float(line)
        rounded = math.floor(amount * 20 + 0.5) / 20
        print(f"{rounded:.2f}")


if __name__ == "__main__":
    main()
