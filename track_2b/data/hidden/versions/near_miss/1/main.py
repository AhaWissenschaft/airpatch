import sys


def key(version):
    parts = [int(p) for p in version.split(".")]
    return parts


def main():
    versions = [line.strip() for line in sys.stdin if line.strip()]
    for v in sorted(versions, key=key):
        print(v)


if __name__ == "__main__":
    main()
