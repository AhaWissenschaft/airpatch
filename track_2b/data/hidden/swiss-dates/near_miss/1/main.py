import re
import sys
from datetime import date

SWISS = re.compile(r"([0-9]{1,2})\.([0-9]{1,2})\.([0-9]{4})")
ISO = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")


DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def valid(y, m, d):
    if not 1 <= m <= 12 or d < 1:
        return False
    limit = DAYS[m - 1] + (1 if m == 2 and y % 4 == 0 else 0)
    return d <= limit


def convert(text):
    m = SWISS.fullmatch(text)
    if m:
        d, mo, y = map(int, m.groups())
        return f"{y:04d}-{mo:02d}-{d:02d}" if valid(y, mo, d) else "invalid"
    m = ISO.fullmatch(text)
    if m:
        y, mo, d = map(int, m.groups())
        return f"{d:02d}.{mo:02d}.{y:04d}" if valid(y, mo, d) else "invalid"
    return "invalid"


def main():
    for line in sys.stdin:
        text = line.strip()
        if text:
            print(convert(text))


if __name__ == "__main__":
    main()
