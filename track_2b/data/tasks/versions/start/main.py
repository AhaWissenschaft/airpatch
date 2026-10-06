import sys


def main():
    versions = [line.strip() for line in sys.stdin if line.strip()]
    for v in sorted(versions):
        print(v)


if __name__ == "__main__":
    main()
