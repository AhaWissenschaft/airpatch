import re
import sys
from datetime import date

SWISS = re.compile(r"([0-9]{1,2})\.([0-9]{1,2})\.([0-9]{4})")
ISO = re.compile(r"([0-9]{4})-([0-9]{2})-([0-9]{2})")


def plausible(y, m, d):
    return 1 <= m <= 12 and 1 <= d <= 31


def convert(text):
    m = SWISS.fullmatch(text)
    if m:
        d, mo, y = map(int, m.groups())
        return f"{y:04d}-{mo:02d}-{d:02d}" if plausible(y, mo, d) else "invalid"
    m = ISO.fullmatch(text)
    if m:
        y, mo, d = map(int, m.groups())
        return f"{d:02d}.{mo:02d}.{y:04d}" if plausible(y, mo, d) else "invalid"
    return "invalid"


def main():
    for line in sys.stdin:
        text = line.strip()
        if text:
            print(convert(text))


if __name__ == "__main__":
    main()
