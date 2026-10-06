import sys
from datetime import date, timedelta


def minutes(text):
    h, m = text.split(":")
    return int(h) * 60 + int(m)


def clock(total):
    return f"{total // 60:02d}:{total % 60:02d}"


def parse(text):
    y, m, d = map(int, text.split("-"))
    return date(y, m, d)


def main():
    busy, pad = {}, 0
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        key = parts[0]
        if key == "days":
            first, last = parse(parts[1]), parse(parts[2])
        elif key == "hours":
            open_at, close_at = minutes(parts[1]), minutes(parts[2])
        elif key == "duration":
            need = int(parts[1])
        elif key == "buffer":
            pad = int(parts[1])
        elif key == "busy":
            busy.setdefault(parts[2], []).append((minutes(parts[3]), minutes(parts[4])))
    day = first
    while day <= last:
        if day.weekday() < 5:
            slots = []
            cursor = open_at
            for start, end in sorted(busy.get(day.isoformat(), [])):
                start, end = start - pad, end + pad
                if start > cursor:
                    slots.append((cursor, min(start, close_at)))
                cursor = max(cursor, end)
            if cursor < close_at:
                slots.append((cursor, close_at))
            kept = [f"{clock(a)}-{clock(b)}" for a, b in slots if b - a >= need]
            print(day.isoformat(), " ".join(kept) if kept else "none")
        day += timedelta(days=1)


if __name__ == "__main__":
    main()
