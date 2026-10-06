import sys
from datetime import date


def minutes(text):
    h, m = text.split(":")
    return int(h) * 60 + int(m)


def hm(total):
    return f"{total // 60}:{total % 60:02d}"


def signed(total):
    return ("-" if total < 0 else "+") + hm(abs(total))


def main():
    targets, weeks = {}, {}
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "target":
            targets[parts[1]] = minutes(parts[2])
            continue
        name, day, start, end = parts
        y, m, d = map(int, day.split("-"))
        _, iso_week, _ = date(y, m, d).isocalendar()
        iso_year = y
        worked = minutes(end) - minutes(start)
        if worked < 0:
            worked += 24 * 60
        key = (name, iso_year, iso_week)
        weeks[key] = weeks.get(key, 0) + worked
    for name in sorted({key[0] for key in weeks}):
        target = targets.get(name, 40 * 60)
        overtime = 0
        for key in sorted(k for k in weeks if k[0] == name):
            diff = weeks[key] - target
            overtime += max(diff, 0)
            print(f"{name} {key[1]}-W{key[2]:02d} {hm(weeks[key])} {signed(diff)}")
        print(f"{name} overtime {hm(overtime)}")


if __name__ == "__main__":
    main()
