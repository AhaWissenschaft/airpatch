import sys
from datetime import date, timedelta


def parse(text):
    y, m, d = map(int, text.split("-"))
    return date(y, m, d)


def main():
    holidays = set()
    allowance = {}
    used = {}
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "holiday":
            holidays.add(parse(parts[1]))
        elif parts[0] == "allowance":
            allowance[parts[1]] = int(parts[2])
        elif parts[0] == "leave":
            first, last = parse(parts[2]), parse(parts[3])
            count = 0
            for offset in range((last - first).days):
                day = first + timedelta(days=offset)
                if day.weekday() < 5 and day not in holidays:
                    count += 1
            used[parts[1]] = used.get(parts[1], 0) + count
    for name in sorted(used):
        print(f"{name} used {used[name]} left {allowance.get(name, 0) - used[name]}")


if __name__ == "__main__":
    main()
