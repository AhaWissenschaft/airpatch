import sys


def main():
    seen = set()
    for raw in sys.stdin:
        text = raw.strip()
        key = text.lower()
        if not text or key in seen:
            continue
        seen.add(key)
        print(text)


if __name__ == "__main__":
    main()
