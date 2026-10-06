import sys

VALUES = [(1000, "M"), (500, "D"), (100, "C"), (50, "L"), (10, "X"), (5, "V"), (1, "I")]


def to_roman(n):
    out = []
    for value, letter in VALUES:
        while n >= value:
            out.append(letter)
            n -= value
    return "".join(out)


def main():
    for line in sys.stdin:
        if line.strip():
            print(to_roman(int(line)))


if __name__ == "__main__":
    main()
