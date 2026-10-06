import sys


def minutes(text):
    h, m = text.split(":")
    return int(h) * 60 + int(m)


def main():
    active = {}
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "book":
            bid, room, day, start, end = parts[1:]
            start, end = minutes(start), minutes(end)
            if end <= start:
                print("INVALID", bid)
                continue
            clashes = [(s, other) for other, (r, d, s, e) in active.items()
                       if r == room and d == day and s < end and start < e]
            if clashes:
                print("REJECT", bid, clashes[0][1])
            else:
                active[bid] = (room, day, start, end)
                print("ACCEPT", bid)
        elif parts[0] == "cancel":
            bid = parts[1]
            if bid in active:
                del active[bid]
                print("CANCELLED", bid)
            else:
                print("UNKNOWN", bid)
    rooms = {}
    for room, _, start, end in active.values():
        count, total = rooms.get(room, (0, 0))
        rooms[room] = (count + 1, total + end - start)
    for room in sorted(rooms):
        count, total = rooms[room]
        print(f"{room} {count} {total // 60}:{total % 60:02d}")


if __name__ == "__main__":
    main()
