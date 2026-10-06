import sys


def main():
    lines = sys.stdin.read().splitlines()
    capacity = int(lines[0])
    cache = {}
    for line in lines[1:]:
        parts = line.split()
        if not parts:
            continue
        if parts[0] == "put":
            if len(cache) >= capacity:
                oldest = next(iter(cache))
                del cache[oldest]
                print("evict", oldest)
            cache[parts[1]] = parts[2]
        elif parts[0] == "get":
            print(cache.get(parts[1], "miss"))
        elif parts[0] == "dump":
            print(" ".join(cache) if cache else "empty")


if __name__ == "__main__":
    main()
