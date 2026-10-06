import sys
from collections import deque


def main():
    grid = [line.rstrip("\n") for line in sys.stdin if line.strip()]
    rows = len(grid)
    cols = len(grid[0]) if grid else 0
    start = None
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "S":
                start = (r, c)
    dist = {start: 0}
    queue = deque([start])
    while queue:
        r, c = queue.popleft()
        if grid[r][c] == "E":
            print(dist[(r, c)])
            return
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] != "#" and (nr, nc) not in dist:
                dist[(nr, nc)] = dist[(r, c)] + 1
                queue.append((nr, nc))
    print("NO PATH")


if __name__ == "__main__":
    main()
