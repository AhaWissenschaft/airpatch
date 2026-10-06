import sys

VALUES = [(1000, "M"), (500, "D"), (100, "C"), (50, "L"), (10, "X"), (9, "IX"),
          (5, "V"), (4, "IV"), (1, "I")]


def to_roman(n):
    out = []
    for value, letters in VALUES:
        while n >= value:
            out.append(letters)
            n -= value
    return "".join(out)


def main():
    for line in sys.stdin:
        if line.strip():
            print(to_roman(int(line)))


if __name__ == "__main__":
    main()
