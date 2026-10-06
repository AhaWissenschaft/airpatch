import sys
from datetime import datetime


def convert(text):
    for fmt_in, fmt_out in (("%d.%m.%Y", "%Y-%m-%d"), ("%Y-%m-%d", "%d.%m.%Y")):
        try:
            return datetime.strptime(text, fmt_in).strftime(fmt_out)
        except ValueError:
            pass
    return "invalid"


def main():
    for line in sys.stdin:
        text = line.strip()
        if text:
            print(convert(text))


if __name__ == "__main__":
    main()
