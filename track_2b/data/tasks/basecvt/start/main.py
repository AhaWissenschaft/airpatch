import sys

DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def to_base(n, base):
    out = ""
    while n > 0:
        out = DIGITS[n % base] + out
        n //= base
    return out


def main():
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        number, src, dst = parts
        src, dst = int(src), int(dst)
        if not (2 <= src <= 36 and 2 <= dst <= 36):
            print("ERROR")
            continue
        try:
            value = int(number, src)
        except ValueError:
            print("ERROR")
            continue
        print(to_base(value, dst))


if __name__ == "__main__":
    main()
