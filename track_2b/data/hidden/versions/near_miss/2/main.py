import sys


def key(version):
    head = version.split(".")[:2]
    return float(".".join(head))


def main():
    versions = [line.strip() for line in sys.stdin if line.strip()]
    for v in sorted(versions, key=key):
        print(v)


if __name__ == "__main__":
    main()
