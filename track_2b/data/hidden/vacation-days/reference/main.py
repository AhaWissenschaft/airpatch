import sys
from datetime import date, timedelta


def parse(text):
    y, m, d = map(int, text.split("-"))
    return date(y, m, d)


def main():
    holidays, allowance, requests = set(), {}, []
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "holiday":
            holidays.add(parse(parts[1]))
        elif parts[0] == "allowance":
            allowance[parts[1]] = int(parts[2])
        elif parts[0] == "leave":
            requests.append((parts[1], parse(parts[2]), parse(parts[3])))
    days = {}
    for name, first, last in requests:
        taken = days.setdefault(name, set())
        day = first
        while day <= last:
            if day.weekday() < 5 and day not in holidays:
                taken.add(day)
            day += timedelta(days=1)
    for name in sorted(set(allowance) | set(days)):
        used = len(days.get(name, ()))
        rest = allowance.get(name, 0) - used
        if rest >= 0:
            print(f"{name} used {used} left {rest}")
        else:
            print(f"{name} used {used} over {-rest}")


if __name__ == "__main__":
    main()
