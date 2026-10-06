import heapq
import sys


def minutes(text):
    h, m = text.split(":")
    return int(h) * 60 + int(m)


def earliest(conns, change, src, dst, t0):
    if src == dst:
        return t0
    dist = {(src, ""): t0}
    heap = [(t0, src, "")]
    while heap:
        t, station, train = heapq.heappop(heap)
        if dist[(station, train)] < t:
            continue
        if station == dst:
            return t
        for c_train, c_to, dep, arr in conns.get(station, []):
            need = t if train == "" else t + change
            if dep >= need and arr < dist.get((c_to, c_train), 10 ** 9):
                dist[(c_to, c_train)] = arr
                heapq.heappush(heap, (arr, c_to, c_train))
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
