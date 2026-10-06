import sys


def main():
    lines = [line.split() for line in sys.stdin.read().splitlines() if line.strip()]
    k = int(lines[0][0])
    customers = []
    for index, parts in enumerate(lines[1:]):
        name, arrival, duration, patience = parts[0], int(parts[1]), int(parts[2]), int(parts[3])
        customers.append((arrival, index, name, duration, patience))
    customers.sort()
    free_at = [0] * k
    served = left = max_wait = 0
    for arrival, _, name, duration, patience in customers:
        start = max(arrival, min(free_at))
        if start - arrival >= patience:
            print(name, "left")
            left += 1
            continue
        counter = min(c for c in range(k) if free_at[c] <= start)
        free_at[counter] = start + duration
        print(name, counter + 1, start, start + duration)
        served += 1
        max_wait = max(max_wait, start - arrival)
    print("served", served, "left", left, "max wait", max_wait)


if __name__ == "__main__":
    main()
