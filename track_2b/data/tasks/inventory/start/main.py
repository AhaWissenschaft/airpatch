import sys


def main():
    stock = {}
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        cmd = parts[0]
        if cmd == "add":
            stock[parts[1]] = stock.get(parts[1], 0) + int(parts[2])
        elif cmd == "remove":
            stock[parts[1]] -= int(parts[2])
        elif cmd == "count":
            print(parts[1], stock[parts[1]])
        elif cmd == "report":
            for item, units in stock.items():
                print(item, units)


if __name__ == "__main__":
    main()
