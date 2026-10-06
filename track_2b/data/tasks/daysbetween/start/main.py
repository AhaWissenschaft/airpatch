import sys

MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def day_number(text):
    y, m, d = map(int, text.split("-"))
    return y * 365 + sum(MONTH_DAYS[:m - 1]) + d


def main():
    for line in sys.stdin:
        if line.strip():
            a, b = line.split()
            print(day_number(b) - day_number(a))


if __name__ == "__main__":
    main()
