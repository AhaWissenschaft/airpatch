import sys


def main():
    bookings = []
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "book":
            bid, room, day, start, end = parts[1:]
            conflict = None
            for other, r, d, s, e in bookings:
                if r == room and s <= start < e:
                    conflict = other
                    break
            if conflict:
                print("REJECT", bid, conflict)
            else:
                bookings.append((bid, room, day, start, end))
                print("ACCEPT", bid)
        elif parts[0] == "cancel":
            bookings = [b for b in bookings if b[0] != parts[1]]
            print("CANCELLED", parts[1])
    rooms = {}
    for bid, room, day, start, end in bookings:
        rooms[room] = rooms.get(room, 0) + 1
    for room in sorted(rooms):
        print(room, rooms[room])


if __name__ == "__main__":
    main()
