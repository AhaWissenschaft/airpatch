import sys

MONTH_DAYS = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def is_leap(y):
    return y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)


def day_number(text):
    y, m, d = map(int, text.split("-"))
    days = sum(366 if is_leap(k) else 365 for k in range(1, y))
    days += sum(MONTH_DAYS[:m - 1]) + d
    if is_leap(y):
        days += 1
    return days


def main():
    for line in sys.stdin:
        if line.strip():
            a, b = line.split()
            print(day_number(b) - day_number(a))


if __name__ == "__main__":
    main()
