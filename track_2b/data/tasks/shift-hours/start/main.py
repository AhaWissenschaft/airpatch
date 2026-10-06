import sys


def minutes(text):
    h, m = text.split(":")
    return int(h) * 60 + int(m)


def main():
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        name, start, end = parts
        worked = minutes(end) - minutes(start)
        if worked > 6 * 60:
            worked -= 30
        print(f"{name} {worked // 60}:{worked % 60:02d}")


if __name__ == "__main__":
    main()
