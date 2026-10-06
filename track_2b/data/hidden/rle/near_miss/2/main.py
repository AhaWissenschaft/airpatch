import sys
from collections import Counter


def encode(s):
    return "".join(ch + str(n) for ch, n in Counter(s).items())


def main():
    for line in sys.stdin:
        print(encode(line.rstrip("\n")))


if __name__ == "__main__":
    main()
