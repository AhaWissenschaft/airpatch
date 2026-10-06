import sys


def minutes(text):
    h, m = text.split(":")
    return int(h) * 60 + int(m)


def main():
    totals = {}
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        plate, _, entry, _, leave = parts
        duration = minutes(leave) - minutes(entry)
        if duration < 0:
            print(plate, "invalid")
            continue
        fee = 0.0
        if duration > 30:
            blocks = duration // 60 + 1
            fee = min(blocks * 2.5, 18.0)
        totals[plate] = totals.get(plate, 0) + fee
        print(f"{plate} {duration // 60}:{duration % 60:02d} {fee:.2f}")
    print("---")
    for plate in sorted(totals):
        print(plate, f"{totals[plate]:.2f}")


if __name__ == "__main__":
    main()
