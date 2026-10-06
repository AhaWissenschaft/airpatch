import heapq
import sys


def main():
    jobs = []
    for line in sys.stdin:
        parts = line.split()
        if parts:
            jobs.append((int(parts[1]), parts[0], int(parts[2]), int(parts[3])))
    jobs.sort()
    time = idle = 0
    ready = []
    i = 0
    while i < len(jobs) or ready:
        if not ready and jobs[i][0] > time:
            idle += jobs[i][0] - time
            time = jobs[i][0]
        while i < len(jobs) and jobs[i][0] <= time:
            arrival, name, duration, priority = jobs[i]
            heapq.heappush(ready, (-priority, arrival, name, duration))
            i += 1
        _, _, name, duration = heapq.heappop(ready)
        print(name, time, time + duration)
        time += duration
    print("idle", idle)


if __name__ == "__main__":
    main()
