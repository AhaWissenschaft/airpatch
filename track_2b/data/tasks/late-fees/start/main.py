import sys
from datetime import date

RATE = {"book": 0.5, "dvd": 1.0, "magazine": 0.2}


def parse(text):
    y, m, d = map(int, text.split("-"))
    return date(y, m, d)


def main():
    lines = sys.stdin.read().splitlines()
    totals = {}
    for line in lines[1:]:
        if not line.strip():
            continue
        member, kind, due, back = line.split()
        if back == "-":
            continue
        late = (parse(back) - parse(due)).days - 3
        if late > 0:
            totals[member] = totals.get(member, 0) + late * RATE[kind]
    for member in sorted(totals):
        print(f"{member} {totals[member]:.2f}")
    print(f"total {sum(totals.values()):.2f}")


if __name__ == "__main__":
    main()
