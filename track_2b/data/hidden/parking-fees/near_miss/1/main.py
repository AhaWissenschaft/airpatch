import sys
from datetime import datetime, timedelta

DAY_RATE, NIGHT_RATE, PERIOD_CAP = 250, 100, 1800


def stamp(day, clock):
    return datetime.strptime(f"{day} {clock}", "%Y-%m-%d %H:%M")


def fee(entry, minutes):
    if minutes <= 30:
        return 0
    blocks = minutes // 60 + 1
    total = 0
    for first in range(0, blocks, 24):
        period = 0
        for k in range(first, min(first + 24, blocks)):
            start = entry + timedelta(minutes=60 * k)
            period += DAY_RATE if 8 <= start.hour < 20 else NIGHT_RATE
        total += min(period, PERIOD_CAP)
    return total


def money(cents):
    return f"{cents // 100}.{cents % 100:02d}"


def main():
    plates = {}
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        plate = parts[0]
        entry, leave = stamp(parts[1], parts[2]), stamp(parts[3], parts[4])
        if leave < entry:
            print(plate, "invalid")
            continue
        minutes = int((leave - entry).total_seconds()) // 60
        cents = fee(entry, minutes)
        stays, total = plates.get(plate, (0, 0))
        plates[plate] = (stays + 1, total + cents)
        print(f"{plate} {minutes // 60}:{minutes % 60:02d} {money(cents)}")
    print("---")
    for plate in sorted(plates, key=lambda p: (-plates[p][1], p)):
        stays, total = plates[plate]
        print(plate, stays, money(total))


if __name__ == "__main__":
    main()
