import sys


def main():
    unique = set()
    for line in sys.stdin:
        key = line.strip().lower()
        if key:
            unique.add(key)
    for key in sorted(unique):
        print(key)


if __name__ == "__main__":
    main()
