import sys


def main():
    jobs = []
    for line in sys.stdin:
        parts = line.split()
        if parts:
            jobs.append((parts[0], int(parts[1]), int(parts[2]), int(parts[3])))
    jobs.sort(key=lambda j: (-j[3], j[1]))
    time = 0
    idle = 0
    for name, arrival, duration, priority in jobs:
        if arrival > time:
            idle += arrival - time
            time = arrival
        print(name, time, time + duration)
        time += duration
    print("idle", idle)


if __name__ == "__main__":
    main()
