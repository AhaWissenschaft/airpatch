import sys

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
VALUE = {ch: i for i, ch in enumerate(DIGITS)}
VALUE.update({ch.lower(): i for ch, i in list(VALUE.items())})


def parse_base(text):
    if text and all(ch in "0123456789" for ch in text):
        base = int(text)
        if 2 <= base <= 36:
            return base
    return None


def parse_number(text, base):
    try:
        return int(text, base)
    except ValueError:
        return None
    negative = text.startswith("-")
    if negative:
        text = text[1:]
    if not text:
        return None
    value = 0
    for ch in text:
        digit = VALUE.get(ch)
        if digit is None or digit >= base:
            return None
        value = value * base + digit
    return -value if negative else value


def to_base(value, base):
    if value == 0:
        return "0"
    sign = "-" if value < 0 else ""
    value = abs(value)
    out = []
    while value:
        value, digit = divmod(value, base)
        out.append(DIGITS[digit])
    return sign + "".join(reversed(out))


def main():
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        if len(parts) != 3:
            print("ERROR")
            continue
        number, src, dst = parts
        src, dst = parse_base(src), parse_base(dst)
        value = parse_number(number, src) if src and dst else None
        print("ERROR" if value is None else to_base(value, dst))


if __name__ == "__main__":
    main()
