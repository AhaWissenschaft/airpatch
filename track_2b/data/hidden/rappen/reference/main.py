import sys
from fractions import Fraction


def round_to_rappen(text):
    value = Fraction(text)
    steps = int(abs(value) * 20 + Fraction(1, 2))
    cents = steps * 5
    sign = "-" if value < 0 and cents else ""
    return f"{sign}{cents // 100}.{cents % 100:02d}"


def main():
    for line in sys.stdin:
        text = line.strip()
        if text:
            print(round_to_rappen(text))


if __name__ == "__main__":
    main()
