import sys


def check_digit(digits):
    total = 0
    for i, ch in enumerate(digits):
        if i % 2 == 0:
            total += int(ch) * 3
        else:
            total += int(ch)
    return 10 - total % 10


def fmt(d):
    return f"{d[0:3]}.{d[3:7]}.{d[7:11]}.{d[11:13]}"


def main():
    for line in sys.stdin:
        digits = line.strip().replace(".", "")
        if len(digits) == 13:
            if check_digit(digits[:12]) == int(digits[12]):
                print("VALID", fmt(digits))
            else:
                print("INVALID", check_digit(digits[:12]))
        elif len(digits) == 12:
            print("COMPLETE", fmt(digits + str(check_digit(digits))))
        else:
            print("ERROR")


if __name__ == "__main__":
    main()
