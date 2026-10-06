import sys
from datetime import date, timedelta

RATE = {"book": 50, "dvd": 100, "magazine": 20}
CAP = 1000
GRACE = 3


def parse(text):
    y, m, d = map(int, text.split("-"))
    return date(y, m, d)


def fee(kind, due, back):
    if due.weekday() == 6:
        due += timedelta(days=1)
    late = (back - due).days
    if late <= GRACE:
        return 0
    return late * RATE[kind]


def money(cents):
    return f"{cents // 100}.{cents % 100:02d}"


def main():
    lines = [line.split() for line in sys.stdin if line.strip()]
    asof = parse(lines[0][1])
    totals = {}
    for member, kind, due, back in lines[1:]:
        back = asof if back == "-" else parse(back)
        totals[member] = min(totals.get(member, 0) + fee(kind, parse(due), back), CAP)
    for member in sorted(totals):
        print(member, money(totals[member]))
    print("total", money(sum(totals.values())))


if __name__ == "__main__":
    main()
