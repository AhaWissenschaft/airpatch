FILE: main.py
```python
import sys


def main():
    stock = {}
    for line in sys.stdin:
        parts = line.split()
        if not parts:
            continue
        cmd, args = parts[0], parts[1:]
        if cmd == "add" and len(args) == 2:
            stock[args[0]] = stock.get(args[0], 0) + int(args[1])
        elif cmd == "remove" and len(args) == 2:
            have, want = stock.get(args[0], 0), int(args[1])
            if want > have:
                print(f"ERROR not enough {args[0]}")
            stock[args[0]] = max(0, have - want)
        elif cmd == "count" and len(args) == 1:
            print(args[0], stock.get(args[0], 0))
        elif cmd == "report" and not args:
            for item in sorted(stock):
                if stock[item] > 0:
                    print(item, stock[item])
            print("total", sum(stock.values()))
        else:
            print("ERROR unknown command")


if __name__ == "__main__":
    main()
```
