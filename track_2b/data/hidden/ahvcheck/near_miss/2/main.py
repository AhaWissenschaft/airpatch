import sys


def check_digit(digits):
    total = sum(int(ch) * (1 if i % 2 == 0 else 3) for i, ch in enumerate(digits))
    return 10 - total % 10


def fmt(digits):
    return f"{digits[:3]}.{digits[3:7]}.{digits[7:11]}.{digits[11:]}"


def classify(text):
    digits = text.replace(".", "").replace(" ", "")
    if not digits or any(ch not in "0123456789" for ch in digits) or not digits.startswith("756"):
        return "ERROR"
    if len(digits) == 12:
        return "COMPLETE " + fmt(digits + str(check_digit(digits)))
    if len(digits) == 13:
        expected = check_digit(digits[:12])
        if int(digits[12]) == expected:
            return "VALID " + fmt(digits)
        return f"INVALID {expected}"
    return "ERROR"


def main():
    for line in sys.stdin:
        text = line.strip()
        if text:
            print(classify(text))


if __name__ == "__main__":
    main()
