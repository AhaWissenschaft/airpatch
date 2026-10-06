import sys


def encode(s):
    out = []
    count = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1]:
            count += 1
        else:
            out.append(s[i - 1] + str(count))
            count = 1
    return "".join(out)


def main():
    for line in sys.stdin:
        print(encode(line.rstrip("\n")))


if __name__ == "__main__":
    main()
