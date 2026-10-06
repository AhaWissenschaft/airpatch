import sys


def main():
    lines = sys.stdin.read().split("\n")
    k = int(lines[0])
    free_at = [0] * k
    served = left = max_wait = 0
    for line in lines[1:]:
        parts = line.split()
        if not parts:
            continue
        name, arrival, duration, patience = parts[0], int(parts[1]), int(parts[2]), int(parts[3])
        counter = free_at.index(min(free_at))
        start = max(arrival, free_at[counter])
        wait = start - arrival
        if wait > patience:
            print(name, "left")
            left += 1
            continue
        free_at[counter] = start + duration
        print(name, counter + 1, start, start + duration)
        served += 1
        max_wait = max(max_wait, wait)
    print("served", served, "left", left, "max wait", max_wait)


if __name__ == "__main__":
    main()
