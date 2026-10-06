import sys
from datetime import datetime


def minutes(text):
    h, m = text.split(":")
    return int(h) * 60 + int(m)


def hm(total):
    return f"{total // 60}:{total % 60:02d}"


def main():
    target = {}
    weeks = {}
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "target":
            target[parts[1]] = minutes(parts[2])
            continue
        name, day, start, end = parts
        week = datetime.strptime(day, "%Y-%m-%d").strftime("%Y-W%W")
        key = (name, week)
        weeks[key] = weeks.get(key, 0) + minutes(end) - minutes(start)
    balance = {}
    for name, week in sorted(weeks):
        diff = weeks[(name, week)] - target.get(name, 40 * 60)
        balance[name] = balance.get(name, 0) + diff
        sign = "+" if diff >= 0 else "-"
        print(f"{name} {week} {hm(weeks[(name, week)])} {sign}{hm(abs(diff))}")
    for name in sorted(balance):
        print(f"{name} overtime {hm(max(balance[name], 0))}")


if __name__ == "__main__":
    main()
