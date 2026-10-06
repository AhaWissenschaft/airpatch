import heapq
import sys


def minutes(text):
    h, m = text.split(":")
    return int(h) * 60 + int(m)


def earliest(conns, change, src, dst, t0):
    best = {src: t0}
    came_with = {src: None}
    heap = [(t0, src)]
    while heap:
        t, station = heapq.heappop(heap)
        if t > best[station]:
            continue
        if station == dst:
            return t
        for train, to, dep, arr in conns.get(station, []):
            if came_with[station] is None or train == came_with[station]:
                need = t
            else:
                need = t + change
            if dep >= need and arr < best.get(to, 10 ** 9):
                best[to] = arr
                came_with[to] = train
                heapq.heappush(heap, (arr, to))
    return None


def main():
    lines = [line.split() for line in sys.stdin.read().splitlines() if line.strip()]
    change = int(lines[0][0])
    conns = {}
    for parts in lines[1:]:
        if parts[0] == "?":
            t = earliest(conns, change, parts[1], parts[2], minutes(parts[3]))
            print("impossible" if t is None else f"{t // 60:02d}:{t % 60:02d}")
        else:
            train, src, dst, dep, arr = parts
            conns.setdefault(src, []).append((train, dst, minutes(dep), minutes(arr)))


if __name__ == "__main__":
    main()
