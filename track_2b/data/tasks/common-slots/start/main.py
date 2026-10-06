import sys
from datetime import date, timedelta


def minutes(text):
    h, m = text.split(":")
    return int(h) * 60 + int(m)


def clock(total):
    return f"{total // 60:02d}:{total % 60:02d}"


def main():
    settings = {}
    busy = {}
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "busy":
            who, day, start, end = parts[1:]
            busy.setdefault((who, day), []).append((minutes(start), minutes(end)))
        else:
            settings[parts[0]] = parts[1:]
    first = date.fromisoformat(settings["days"][0])
    last = date.fromisoformat(settings["days"][1])
    open_at, close_at = (minutes(t) for t in settings["hours"])
    need = int(settings["duration"][0])
    day = first
    while day <= last:
        key = day.isoformat()
        taken = sorted(busy.get(("A", key), []) + busy.get(("B", key), []))
        slots = []
        cursor = open_at
        for start, end in taken:
            if start - cursor >= need:
                slots.append(f"{clock(cursor)}-{clock(start)}")
            cursor = end
        if close_at - cursor >= need:
            slots.append(f"{clock(cursor)}-{clock(close_at)}")
        print(key, " ".join(slots) or "none")
        day += timedelta(days=1)


if __name__ == "__main__":
    main()
