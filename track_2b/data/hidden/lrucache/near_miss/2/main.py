import sys
from collections import OrderedDict


def main():
    lines = sys.stdin.read().splitlines()
    capacity = int(lines[0])
    cache = OrderedDict()
    for line in lines[1:]:
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "put":
            key, value = parts[1], parts[2]
            if len(cache) >= capacity:
                old, _ = cache.popitem(last=False)
                print("evict", old)
            cache[key] = value
            cache.move_to_end(key)
        elif parts[0] == "get":
            if parts[1] in cache:
                cache.move_to_end(parts[1])
                print(cache[parts[1]])
            else:
                print("miss")
        elif parts[0] == "dump":
            print(" ".join(reversed(cache)) if cache else "empty")


if __name__ == "__main__":
    main()
