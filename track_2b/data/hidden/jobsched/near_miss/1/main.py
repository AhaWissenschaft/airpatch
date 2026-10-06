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
        if not ready:
            if jobs[i][0] > time:
                idle += jobs[i][0] - time
                time = jobs[i][0]
            while i < len(jobs) and jobs[i][0] <= time:
                ready.append(jobs[i])
                i += 1
        ready.sort(key=lambda j: (-j[3], j[0], j[1]))
        arrival, name, duration, priority = ready.pop(0)
        print(name, time, time + duration)
        time += duration
        while i < len(jobs) and jobs[i][0] < time:
            ready.append(jobs[i])
            i += 1
    print("idle", idle)


if __name__ == "__main__":
    main()
