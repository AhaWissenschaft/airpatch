import sys


def minutes(text):
    h, m = text.split(":")
    return int(h) * 60 + int(m)


def paid(start, end):
    worked = end - start
    if worked < 0:
        worked += 24 * 60
    if worked > 9 * 60:
        worked -= 45
    elif worked > 6 * 60:
        worked -= 30
    return worked


def main():
    totals = {}
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        name, start, end = parts
        totals[name] = totals.get(name, 0) + paid(minutes(start), minutes(end))
    for name in sorted(totals):
        hours, mins = divmod(totals[name], 60)
        print(f"{name} {hours}:{mins:02d}")


if __name__ == "__main__":
    main()
